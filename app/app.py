import math
import os
import random
import asynckivy

from kivy.clock import Clock, mainthread
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.metrics import dp, sp
from kivy.properties import ColorProperty
from kivy.storage.jsonstore import JsonStore
from kivy.uix.screenmanager import CardTransition, ScreenManager
from kivy.utils import QueryDict, hex_colormap, platform, rgba
from kivymd.app import MDApp
from kivymd.uix.bottomsheet import MDCustomBottomSheet

from controllers.home import ExpenseList, UpdateBudgetContent
from utils.androidly import Storage
from models.database import DatabaseManager
from models.firebase_db import FirebaseManager
from utils.popup_items import icons
from utils.send_mail import send_email
from utils.today import date_dict, today_date
from widgets import notify
from widgets.button import FlatButton, RoundButton
from widgets.popup import Pop

# TODO: You may know an easier way to get the size of a computer display.


# @mainthread


class WindowManager(ScreenManager):
    pass


class Moneywatch(MDApp):

    primary = ColorProperty()
    bg = ColorProperty()

    secondary = ColorProperty()

    warning = ColorProperty()
    danger = ColorProperty()

    success = ColorProperty()
    white = ColorProperty()
    textfield_text = ColorProperty()
    icon_color = ColorProperty()
    text_color = ColorProperty()

    orange = ColorProperty()
    black = ColorProperty()
    grey = ColorProperty()
    grey2 = ColorProperty()

    fonts = QueryDict()
    fonts.heading = 'assets/fonts/Poppins-SemiBold.ttf'
    fonts.subheading = 'assets/fonts/Poppins-Regular.ttf'
    fonts.body = 'assets/fonts/Poppins-Medium.ttf'

    fonts.size = QueryDict()
    fonts.size.heading = sp(30)
    fonts.size.icon = sp(30)
    fonts.size.h1 = sp(24)
    fonts.size.h2 = sp(22)
    fonts.size.h3 = sp(18)
    fonts.size.h4 = sp(16)
    fonts.size.h5 = sp(14)
    fonts.size.h6 = sp(12)
    fonts.size.h7 = sp(5)
    fonts.size.bar = sp(3)

    images = QueryDict()

    def __init__(self, **kwargs):
        """
        The __init__ function is called when an instance of a class is created.
        It can be used to set up variables and attributes that the object will use later on.


        :param self: Refer to the current instance of the class
        :param **kwargs: Pass a keyworded, variable-length argument list
        :return: None
        :doc-author: Trelent
        """

        super().__init__(**kwargs)
        self.wm = WindowManager()
        self.path = Storage().storage()

        self.screens_store = JsonStore(f"models/screens.json")

        self.screen_history = []

        self.theme_store = JsonStore(f"models/theme.json")

        self.amount_store = JsonStore(f"{self.path}/expenses.json")

        self.current = str(today_date).split("-")
        self.month_year = f"{self.current[0]}-{self.current[1]}"

        self.sql_db = DatabaseManager()
        self.conn = self.sql_db.conn
        self.cursor = self.conn.cursor()

        self.firebase_manager = FirebaseManager()

        self.db = self.firebase_manager.db

        self.notify = notify.Notify()

        if not self.theme_store.exists("theme"):
            self.theme_store.put("theme", current_theme="light")

        self.switch_theme_style(change_theme=False)

        self.change_screen("splash")
        self.t = 180

    def build(self):
        """
        The build function is used to build the app. It returns a ScreenManager
        instance that contains all of your screens, which you can add to by using
        the .add_widget() method. The docstring above it explains what the build function does.

        :param self: Access variables that belongs to the class
        :return: The screenmanager
        :doc-author: Trelent
        """

        # The below block of code removes the burden of entering the email every time you wanna login

        # checks if 'email.txt' exists in file path. I
        if os.path.exists("email.txt"):
            self.change_screen('login', switch=False)

            # If exists, read the content
            with open("email.txt", "r") as email_file:
                email = email_file.read()
        #   insert it into the email field of the login screen.
            self.wm.get_screen(
                "login").ids['email'].text = email

        # set the application theme
        self.theme_cls.material_style = "M3"  # sets material style to M3
        self.theme_cls.set_colors(
            "Pink", "900", "900", "900", "Gray", "900", "900", "900")
        self.theme_cls.theme_style_switch_animation = True

        # switch theme style to the last selected theme by the user
        self.switch_theme_style(change_theme=False)

        # returns the window manager instance
        return self.wm

    def on_start(self):
        """
        The on_start function is called when the app first starts.
        It schedules a function to run after the splash screen has been shown,
        and then waits for that function to finish before returning.

        :param self: Access the attributes and methods of the class inside a method
        :return: The following:
        :doc-author: Trelent
        """
        Clock.schedule_once(lambda ev: self.post_build_init(ev), 1)

        asynckivy.start(self.check_and_upload_to_firebase())
        asynckivy.start(self.check_if_update())
        Clock.schedule_once(lambda x: self.change_screen("login"), 2)

        # if platform == "android":

        # if platform == "android":
        #     self.start_service()

    async def check_if_update(self, *args):
        """
        The check_if_update function is called by the main app class to check if there is an update available.
        If there is, it will change the screen to a new one that displays a message saying that an update has been found and 
        that they should download it from our website. If not, then nothing happens.

        :param self: Access the class attributes and methods
        :param *args: Pass a variable number of arguments to a function
        :return: A value of true or false
        :doc-author: Trelent
        """

        try:
            update_value = await asynckivy.run_in_thread(lambda: self.get_update_value())

            condition = update_value.val()

            if condition == False:
                pass
            else:
                self.change_screen("updateapp")

        except (ConnectionAbortedError, ConnectionError, ConnectionRefusedError, ConnectionResetError) as e:
            print(f" update check error: {e}")
            # self.notify.notify(message="Connection Error", error=True)

        except Exception as e:
            print(f" unexpected error: {e}")

    def get_update_value(self):
        update_value = self.db.child("update").get()
        return update_value

    def post_build_init(self, ev):
        """
        The post_build_init function is called after the build function of the Kivy app. 
        It binds a keyboard event handler to EventLoop.window, which is an instance of WindowBase, 
        a base class for all window implementations in Kivy. The on_keyboard method of EventLoop will be called when a key press occurs.

        :param self: Access the attributes and methods of the class inside a method
        :param ev: Pass the event object to the function
        :return: The function that is bound to the on_keyboard event of the window
        :doc-author: Trelent
        """

        from kivy.base import EventLoop
        EventLoop.window.bind(on_keyboard=self.hook_keyboard)

    def hook_keyboard(self, window, key, *largs):
        """
        The hook_keyboard function is used to capture the escape key and close the application.
        The function checks if the current screen is login or home, if it is then it will pop a exit popup.
        If not, then it will go back to previous screen.

        :param self: Access the class attributes and methods
        :param window: Get access to the window object
        :param key: Check if the user has pressed any key on the keyboard
        :param *largs: Catch all the extra parameters that are passed to the function
        :return: True if the user presses the escape key
        :doc-author: Trelent
        """

        if key == 27:

            print(self.wm.current)
            if(self.wm.current == 'login'):
                self.exit_popup()
            if(self.wm.current == 'home'):
                self.exit_popup()
            else:
                self.goback()
            return True

    def after_splash(self, *args):
        """
        The after_splash function is called after the splash screen has been shown.
        It changes the screen to login.

        :param self: Access the attributes and methods of the class in python
        :param *args: Pass a variable number of arguments to a function
        :return: The login screen
        :doc-author: Trelent
        """

        self.change_screen("login")

    def fetch_budget(self):
        """
        The fetch_budget function is used to fetch the budget of a particular month.
        It takes in no parameters and returns the budget for that month.

        :param self: Access variables that belongs to the class
        :return: The budget of the user for the month
        :doc-author: Trelent
        """
        # try:
        email = self.wm.get_screen("login").ids['email'].text
        email = email.strip()
        email = email.lower()
        # print(f"emaile budget: {email}")
        # except Exception:
        #     self.notify.notify("Unable to get email", error=True)
        sql = "SELECT * FROM budget WHERE email=?"
        # sql = "SELECT * FROM budget WHERE email=? AND strftime('%Y-%m', budget) =?"
        # conn = self.conn
        # cursor = conn.cursor()
        # cursor.execute(sql, (email, ))
        # self.cursor.execute(sql, (email, ))
        self.cursor.execute(sql, (email,))
        # # global result
        result = self.cursor.fetchall()

        # print(f"budget_result: {result}")
        if result:
            for value in result:
                if self.month_year in value[3]:
                    # print(self.month_year)
                    budget = value[2]
                    return budget
                    break

            else:
                return "tada:::: You have not any budget for this month"
        else:
            asynckivy.start(self.fetch_budget_from_firebase(email))

    def get_budgets_value(self):
        budgets_value = self.db.child("budgets").get()
        return budgets_value

    async def fetch_budget_from_firebase(self, email):
        try:
            # res = self.db.child("budgets").get()
            res = await asynckivy.run_in_thread(lambda: self.get_budgets_value())
            # print(f"resval: {res.val()}")
            # print(f"reskey: {res.key()}")

            for values in res.each():
                #     print(f"budgetval: {values.val()}")
                # print(self.month_year)
                # print(f"uservalemail: {user.val()['email']}")
                for value in values.val():

                    budget = values.val()[value]['budget']
                    date = values.val()[value]['date']
                    emails = values.val()[value]['email']

                # email = values.val()['email']
                    if email == emails:
                        # print(f"budget_afetr: {budget}")
                        # print(f"date_afetr: {date}")
                        # print(f"email_afetr: {emails}")
                        sql = "INSERT INTO budget (email, budget, date) VALUES (?,?,?)"
                        self.cursor.execute(sql, (email, budget, date))
                        self.conn.commit()
                        if self.month_year in str(date):
                            budget = values.val()['budget']

                            # print(
                            # f"budget verified = {values.val()['budget']}")
                        # break
                            return budget
            else:
                self.notify.notify("No budget found for this month")
        except (ConnectionAbortedError, ConnectionError, ConnectionRefusedError, ConnectionResetError, Exception) as e:
            print(f" budget error: {e}")

    def ask_delete(self, wid, date, category, amount, *args):
        """
        The ask_delete function is called when the user presses the delete button on a row in the list.
        It creates a popup with two buttons, one to confirm deletion and one to cancel it. 
        The yes_btn calls another function that deletes from database and updates table, while no_btn closes popup.

        :param self: Make the function a method of the class
        :param wid: Identify the widget to be deleted
        :param date: Identify the record to be deleted
        :param category: Delete the category from the database
        :param amount: Delete the amount from the database
        :param *args: Send a non-keyworded variable length argument list to the function
        :return: A pop object
        :doc-author: Trelent
        """

        yes_btn = FlatButton(text="Yes, delete", text_color="#ffffff",  md_bg_color=self.danger,
                             on_press=lambda x: self.execute_yes(wid, date, category, amount))
        no_btn = FlatButton(
            text="No, Please", on_press=lambda *args: self.no(*args))
        # global ask
        self.ask = Pop(title="Delete?", text="Are you sure?",
                       buttons=[yes_btn, no_btn])
        self.ask.open()

    def no(self, obj):
        self.ask.dismiss()

    def execute_yes(self, wid, date, category, amount):
        asynckivy.start(self.yes(wid, date, category, amount))

    async def yes(self, wid, date, category, amount):
        # print(wid.text)
        # print(wid.secondary_text.split(":"))
        # print(wid.tertiary_text)
        self.wm.get_screen(
            "home").ids['expense_container'].remove_widget(wid)

        self.calculate_expenses_and_percentage(if_login=True)

        self.ask.dismiss()
        self.notify.notify("Deleted", error=True)

        email = self.wm.get_screen("login").ids['email'].text
        email = email.strip()

        Clock.schedule_once(lambda x: self.yess(wid, date, category, amount))
        # await asynckivy.run_in_thread(lambda: self.yess(wid, date, category, amount))
        await asynckivy.run_in_thread(lambda: self.firebase_manager.remove_expense(email, amount, category, date))

    def yess(self, wid, date, category, amount):
        """
        The yes function is called when the user clicks on the yes button in
        the popup. It deletes an expense from the database and removes it from
        the screen.

        :param self: Represent the instance of the class
        :param wid: Remove the widget from the screen
        :param date: Get the date of the expense
        :param category: Get the category name and item bought
        :param amount: Get the amount of money spent on a particular item
        :return: Nothing, so the function call in your code is useless
        :doc-author: Trelent
        """
        # print(f"date: {date}")
        # print(f"amount: {amount}")
        splitted = category.split(":")
        category = splitted[0].title()
        category = category.strip()
        item = splitted[1].lower()
        item = item.strip()
        # item = item.strip()
        date = date.strip()
        amount = amount.strip()
        # print(f"category: {category}")
        # print(f"item: {item}")

        # print(f" widget: {wid}")

        email = self.wm.get_screen("login").ids['email'].text
        email = email.strip()
        # sql = "DELETE FROM expenses WHERE email=? AND date = ? AND category_name=? AND item_bought=? AND price=?"
        # executed = self.conn.execute(sql, (email, date, category, item, amount))

        sql = "SELECT (id) FROM expenses WHERE email=? AND item_bought LIKE ? AND price=? AND date=?"
        executed = self.cursor.execute(
            sql, (email.lower(), f'%{item}%', amount, date))
        executed = executed.fetchall()
        # print(f"executed: {executed}")
        # print(executed)
        expense_id = executed[0][0]
        # print(f'expense_id: {expense_id}')

        # print(expense_id)
        sql = "DELETE FROM expenses WHERE id=?"
        self.cursor.execute(sql, (expense_id,))
        # print(expense_id)
        # res = self.cursor.fetchall()
        # print(res)
        self.conn.commit()
        # self.wm.remove_widget(widget=wid)
        # self.wm.get_screen(
        #         "home").ids['expense_container'].remove_widget()
        # self.fetch_expenses()
        Clock.schedule_once(
            lambda x: self.calculate_expenses_and_percentage(if_login=True), 1)

    @mainthread
    def fetch_expenses(self, limited=True):
        """
        The fetch_expenses function fetches all the amount spent for the month from the database

        :param self: Access variables that belongs to the class
        :return: The total amount spent for the month
        :doc-author: Trelent
        """

        """Fetches all the amount spent for the month from the database"""
        email = self.wm.get_screen("login").ids['email'].text
        email = email.lower()
        email = email.strip()

        if limited == True:
            limit = 6
            sql_limited = "SELECT * FROM expenses WHERE email=? AND DATE LIKE ? ORDER BY id DESC LIMIT ?"
            self.cursor.execute(
                sql_limited, (email, f'%{self.month_year}%', limit))
        else:
            sql_unlimited = "SELECT * FROM expenses WHERE email=? AND date LIKE ? ORDER BY id DESC"
            self.cursor.execute(sql_unlimited, (email, f'%{self.month_year}%'))
        # sql_expense = "SELECT price FROM expenses WHERE email=? AND strftime('%Y-%m', price) =?"

        # global result
        result = self.cursor.fetchall()
        self.change_screen("home", switch=False)
        # print(f"expense_result: {result}")
        if result:
            price_list = []

            # self.change_screen("home")
            self.wm.get_screen(
                "home").ids['expense_container'].clear_widgets()
            for value in result:
                if self.month_year in value[5]:
                    # break
                    # for price in result[0]:
                    price = value[3]
                    price_no_comma = value[3]
                    item = value[2]
                    date = value[5]
                    icon = value[4].lower()
                    category = value[4].title()
                    if "," in price_no_comma:
                        price_no_comma = price_no_comma.replace(",", "")
                    price_list.append(int(price_no_comma))

                    self.wm.get_screen(
                        "home").ids['expense_container'].add_widget(ExpenseList(category=category, icon=icons[icon], amount=price, date=date, item=item))
            price = sum(price_list)
            return price
        else:

            try:
                # email = email.replace(".", "-")
                res = self.db.child("expenses").get()

                price_list = []

                for expense in res.each():
                    # print(f"expenseval: {expense.val()}")

                    for value in expense.val():

                        if expense.val()[value]['email'].replace("-", ".") == email and self.month_year in expense.val()[value]['date']:
                            # print(
                            # f" the email: {expense.val()[value]['email']}")
                            # print(f"normal: {email}")

                            # email = expense.val()[value]['email']
                            # email = email.replace("-", ".")
                            # date = expense.val()[value]['date']
                            # print("expenses loading...")
                            price = expense.val()[value]['price']
                            email_gotten = expense.val()[value]['email']
                            date = expense.val()[value]['date']
                            item = expense.val()[value]['item']
                            category = expense.val()[value]['category']
                            price_no_comma = expense.val()[value]['price']
                            icon = category.lower()

                            sql = "INSERT INTO expenses (email, item_bought, price, category_name, date) VALUES (?,?,?,?,?)"
                            self.cursor.execute(
                                sql, (email, item, price, category, date))

                            self.conn.commit()

                            if "," in price_no_comma and self.month_year in date:
                                price_no_comma = price_no_comma.replace(
                                    ",", "")
                            self.wm.get_screen(
                                "home").ids['expense_container'].add_widget(ExpenseList(category=category, icon=icons[icon], amount=price, date=date, item=item))
                            price_list.append(int(price_no_comma))

                            # if self.month_year in date:

                price = sum(price_list)
                return price

            except (ConnectionAbortedError, ConnectionError, ConnectionRefusedError, ConnectionResetError, Exception) as e:
                # self.notify.notify("No internet connection")
                print(f" fetchexpenses error: {e}")
                self.fetch_expenses()

            # print(f"price_sum: {price}")
            # self.amount_store.put("total_expenses", total = price)

    def get_users_value(self):
        users_value = self.db.child("users").get()
        return users_value

    async def login(self, email, password):
        """
        The login function is used to login into the app. It takes in an email and a password as parameters, checks if they are valid and then logs in the user.

        :param self: Access the attributes and methods of the class in python
        :param email: Fetch the email from the database
        :param password: Encrypt the password before storing it in the database
        :return: A list of tuples
        :doc-author: Trelent
        """
        email = email.lower()
        sql = "SELECT * FROM user_info WHERE email=? AND password=?"
        self.cursor.execute(sql, (email.strip(), password.strip()))
        result = self.cursor.fetchall()

        # if the cursor fetches any the result
        if result:
            name = result[0][1]

            if self.fetch_budget() != None:
                await asynckivy.run_in_thread(lambda: self.calculate_expenses_and_percentage(if_login=True))
                self.reset_btn_text_login()
                self.wm.get_screen(
                    "home").ids['greeting'].text = f"Hi, {name.title()} "
                with open("email.txt", "w") as f:
                    f.write(email)
            else:
                self.reset_btn_text_login()
                self.change_screen("budget")
                self.change_screen("home", switch=False)
                self.wm.get_screen(
                    "home").ids['percentage'].text = "0 %"

                self.wm.get_screen(
                    "home").ids['greeting'].text = f"Hi, {name.capitalize()}"

                self.notify.notify(
                    "You have not any budget for this month", error=True)
        elif not result:
            try:
                users_value = await asynckivy.run_in_thread(lambda: self.get_users_value())
                res = users_value
                email = email.lower()
                email = email.strip()
                password = password.strip()

                for user in res.each():
                    if email == user.val()['email'].lower() and password == user.val()['password']:
                        name = user.val()['name']
                        # print(f"name (from firebase): {name}")
                        # break
                        try:
                            email = email.replace("-", ".")
                            sql = "INSERT INTO user_info (username, email,  password) VALUES (?, ?, ?)"
                            self.cursor.execute(
                                sql, (name.lower(), email.lower(), password))
                            self.conn.commit()
                        except:
                            pass
                        if self.fetch_budget() != None:
                            await asynckivy.run_in_thread(lambda: self.calculate_expenses_and_percentage(
                                if_login=True))
                            self.reset_btn_text_login()
                            self.wm.get_screen(
                                "home").ids['greeting'].text = f"Hi, {name.title()} "
                            with open("email.txt", "w") as f:
                                f.write(email)
                            self.reset_btn_text_login()
                            break
                        else:
                            self.reset_btn_text_login()

                            self.change_screen("budget")
                            self.change_screen("home", switch=False)

                            self.notify.notify(
                                "You have not any budget for this month", error=True)
                            self.wm.get_screen(
                                "home").ids['percentage'].text = "0 %"

                            self.wm.get_screen(
                                "home").ids['greeting'].text = f"Hi, {name.capitalize()}"
                            self.reset_btn_text_login()
                else:
                    self.notify.notify("Invalid Email or password", error=True)
                    self.reset_btn_text_login()
            except (ConnectionAbortedError, ConnectionError, ConnectionRefusedError, ConnectionResetError, Exception) as e:
                print(f" login error: {e}")
                self.notify.notify("No internet connection", error=True)
                self.reset_btn_text_login()

        else:
            # firebase_results = self.firebase_manager.fetch_user(email, password)
            # if firebase_results == [email, password]:
            #     print("firebase ")
            # else:
            self.reset_btn_text_login()
            self.notify.notify("User does not exist", error=True)
            # self.reset_btn_text_login()
            # self.notify.notify("invalid email or password", error=True)

    def login_loader(self, email, password):

        self.wm.get_screen('login').ids['btn'].text = "Verifying..."

        asynckivy.start(self.login(email.lower(), password))

    def reset_btn_text_login(self):
        """
        The reset_btn_text_login function resets the text of the login screen's proceed button to &quot;Proceed&quot; after it has been changed by pressing the  button.

        :param self: Access the attributes and methods of the class
        :return: &quot;proceed&quot;
        :doc-author: Trelent
        """

        self.wm.get_screen('login').ids['btn'].text = "Proceed"

    def fetch_total_expenses_from_db(self, *args):
        """
        The fetch_total_expenses_from_db function is used to fetch the total expenses from the database.
        It takes in a string argument of email and returns an integer value of price.

        :param self: Access variables that belongs to the class
        :param *args: Pass a variable number of arguments to a function
        :return: The total expenses for the current month
        :doc-author: Trelent
        """

        email = self.wm.get_screen("login").ids['email'].text
        email = email.lower()
        email = email.strip()

        sql_unlimited = "SELECT price FROM expenses WHERE email=? AND date LIKE ? ORDER BY id"
        self.cursor.execute(sql_unlimited, (email, f'%{self.month_year}%'))
        # sql_expense = "SELECT price FROM expenses WHERE email=? AND strftime('%Y-%m', price) =?"

        # global result
        result = self.cursor.fetchall()
        # print(f"total expenses from db: {result}")
        if result:
            price_list = []

            # self.change_screen("home")

            for value in result:
                # break
                # for price in result[0]:
                price = value[0]
                if "," in price:
                    price = price.replace(",", "")
                # print(price)
                price_list.append(int(price))

            price = sum(price_list)
            # print(f"price_sum: {price}")
            # self.amount_store.put("total_expenses", total = price)
            self.update_expenses(price)
            return price
        else:
            try:
                # email = email.replace(".", "-")
                res = self.db.child("expenses").get()
                # print(f"resval: {res.val()}")
                # print(f"reskey: {res.key()}")
                # print(f"reseach: {res.each()}")

                price_list = []

                for expense in res.each():
                    # print(f"expenseval: {expense.val()}")
                    # print(f"expenseval email: {expense.val()['email']}")
                    for value in expense.val():

                        email_gotten = expense.val()[value]['email']
                        email_gotten = email_gotten.strip()
                        date = expense.val()[value]['date']
                        # print(f"email gotten: {email_gotten}lo")
                        # print(f"email : {email}lo")
                        if email_gotten.replace("-", ".") == email.strip() and self.month_year in date:
                            # print("gotcha")
                            # email = expense.val()['email']
                            # item = expense.val()['item']
                            price = expense.val()[value]['price']
                        # category = expense.val()['category']

                            if "," in price:
                                price = price.replace(",", "")
                            price_list.append(int(price))

                price = sum(price_list)
                # print(f"price_list: {price_list}")
                # print(f"price_sum: {price}")
                # self.amount_store.put("total_expenses", total = price)
                self.update_expenses(price)
                return price
            except (ConnectionAbortedError, ConnectionError, ConnectionRefusedError, ConnectionResetError, Exception) as e:
                self.notify.notify("Error connecting to the internet")
                # print(f" fetchtotalexpenses error: {e}")

    def toggle_amount(self):
        """
        The toggle_amount function is used to toggle the amount of money spent.
        It takes in no parameters and returns an integer value.

        :param self: Access the class attributes and methods
        :return: The total amount of money spent on expenses
        :doc-author: Trelent
        """

        if self.amount_store.exists("total_expenses"):
            total = self.amount_store.get("total_expenses")["total"]
            total = (format(int(total),  ',d'))
            # print(total)

            return total

    def get_total_expenses(self):
        """
        The get_total_expenses function returns the total amount of expenses in the store.


        :param self: Access the attributes and methods of the class in python
        :return: The total amount of expenses in the store
        :doc-author: Trelent
        """

        if self.amount_store.exists("total_expenses"):
            total = self.amount_store.get("total_expenses")["total"]
            return total

    def update_expenses(self, total_expenses):
        """
        The update_expenses function updates the total expenses in the amount_store.


        :param self: Access the attributes and methods of the class in python
        :param total_expenses: Store the total amount of expenses for a given month
        :return: The total_expenses variable
        :doc-author: Trelent
        """

        self.amount_store.put("total_expenses", total=total_expenses)

    @mainthread
    def calculate_expenses_and_percentage(self, if_login: bool, *args):
        """
        The calculate_expenses_and_percentage function is used to calculate the total expenses and percentage of budget spent.
        It takes in a name as an argument, fetches the budget from the database and calculates both total expenses and percentage of budget spent.
        The function then displays these values on screen.

        :param self: Access the class attributes and methods
        :param name: Fetch the name of the user from the database
        :return: The total expenses, the percentage and the budget
        :doc-author: Trelent
        """

        self.change_screen("home", switch=False)

        # asynckivy.start(self.fetch_budget())
        budget = self.fetch_budget()
        # print(f":::::::{budget}")

        if "," in str(budget):
            budget = budget.replace(",", "")
        budget = int(budget)
        if if_login == True:
            # total_expenses = self.get_total_expenses()
            # self.amount_store.clear()
            total_expenses = self.fetch_total_expenses_from_db()
            # Clock.schedule_once(self.fetch_expenses)
            self.fetch_expenses()
        else:
            total_expenses = self.get_total_expenses()
            # Clock.schedule_once(
            # lambda x: self.update_expenses(total_expenses), 2)
        if total_expenses == None:
            total_expenses = 1
            self.notify.notify("You have made no expenses yet", error=True)
            percentage = (total_expenses/budget) * 100
        else:
            percentage = (total_expenses/budget) * 100
        # print(
            # f"tottal: {total_expenses} %: {percentage}%, budget: {budget}")

        self.wm.get_screen(
            "home").ids['limit_bar'].set_value = percentage

        self.wm.get_screen(
            "home").ids['amount'].text = "XXXX.XX NGN"

        self.wm.get_screen(
            "home").ids['month_year'].text = f"{date_dict[self.current[1][1]]}, {self.current[0]}"  # fetches the date and displays it on the homescreen

        if percentage <= 25:

            self.wm.get_screen(
                "home").ids['limit_bar'].bar_color = self.success
            self.wm.get_screen(
                "home").ids['percentage'].text_color = self.success
        if percentage > 25 and percentage <= 50:

            self.wm.get_screen(
                "home").ids['limit_bar'].bar_color = self.yellow
            self.wm.get_screen(
                "home").ids['percentage'].text_color = self.yellow
        if percentage > 50 and percentage <= 75:

            self.wm.get_screen(
                "home").ids['limit_bar'].bar_color = self.orange
            self.wm.get_screen(
                "home").ids['percentage'].text_color = self.orange
        if percentage > 75 and percentage <= 100:

            self.wm.get_screen(
                "home").ids['limit_bar'].bar_color = self.warning
            self.wm.get_screen(
                "home").ids['percentage'].text_color = self.warning

            self.notify.notify(
                f"You have exhausted {str(round(percentage))}% of your budget\n You should reduce your expenses", method="dialog", color="#Ff8c00")

        if percentage > 100:

            self.wm.get_screen(
                "home").ids['limit_bar'].bar_color = self.warning
            self.wm.get_screen(
                "home").ids['percentage'].text_color = self.warning

            self.notify.notify(
                f"You have exhausted {str(round(percentage))}% of your budget\n You have spent more than your allocated budget could account for.", method="dialog", color="#Ff8c00")

        self.wm.get_screen(
            "home").ids['percentage'].text = f"{str(round(percentage))}%"

        self.change_screen("home")
        Clock.schedule_once(self.fetch_total_expenses_from_db, 2)

    def otp_loader(self, email):
        self.wm.get_screen("forgot").ids['btn'].text = "verifying email..."

        asynckivy.start(self.go_to_otp(email))

    async def go_to_otp(self, email):
        """
        The go_to_otp function is used to generate a random OTP and send it to the user's email.
        It also starts a countdown timer that will automatically expire the OTP  if it isn't used on time.

        :param self: Access the class variables
        :param email: Send the otp to the user's email address
        :return: The otp generated by the generate_otp function
        :doc-author: Trelent
        """

        email = email.strip()
        sql = "SELECT * FROM user_info WHERE email = ?"
        self.cursor.execute(sql, (email.lower(),))
        result = self.cursor.fetchall()
        if result:
            otp = str(self.generate_otp())
            self.change_screen("otp")
            self.wm.get_screen("otp").ids['otp_lbl'].text = otp
            # self.wm.get_screen("otp").ids['first'].focus = True
            # print("{self.generate_otp()}")
            # self.change_screen("otp")
            if self.wm.has_screen("otp"):

                # Clock.schedule_once(lambda x: self.change_screen("otp"))
                self.wm.get_screen("forgot").ids['btn'].text = "proceed"
                Clock.schedule_interval(self.countdown, 1)
                await asynckivy.run_in_thread(lambda: self.emailer(email, otp))
        else:
            self.notify.notify("Email not found", error=True)

    def emailer(self, recipient, otp):
        """
        The emailer function sends an email to the recipient with the OTP.


        :param self: Access the class variables
        :param recipient: Specify the email address of the recipient
        :param otp: Store the one time password that is generated by the send_email function
        :return: A print statement
        :doc-author: Trelent
        """

        asynckivy.start(send_email(recipient=recipient, otp=otp))
        # print("Email sent")

    def resend_loader(self):
        self.wm.get_screen("otp").ids['resend_btn'].text = "Resending..."

    async def resend_otp(self):
        """
        The resend_otp function is used to resend the otp to the user's email address.
        It takes in no parameters and returns nothing.

        :param self: Access variables that belongs to the class
        :return: The otp that is generated and sent to the user
        :doc-author: Trelent
        """

        email = self.wm.get_screen("forgot").ids['email'].text.strip()
        # otp = str(self.generate_otp())
        # self.wm.get_screen("otp").ids['otp_lbl'].text = otp
        # self.change_screen("otp", switch=False)
        # if self.wm.has_screen("otp"):

        #     Clock.schedule_once(lambda x: self.emailer(email, otp), 1)
        #     self.change_screen("otp")
        #     Clock.schedule_interval(self.countdown, 1)
        self.t = 180
        otp = str(self.generate_otp())
        self.wm.get_screen("otp").ids['resend_btn'].text = "Resend otp"
        await asynckivy.run_in_thread(lambda: self.emailer(email, otp))

        self.notify.notify("Otp Resent")

    def generate_otp(self):
        """
        The generate_otp function generates an OTP and stores it in a variable.
        It then returns the value of the otp to be used later.

        :param self: Access variables that belongs to the class
        :return: A 4 digit random number
        :doc-author: Trelent
        """

        # Declare a digits variable
        # which stores all digits
        digits = "0123456789"
        OTP = ""

        # length of password can be changed
        # by changing value in range
        for i in range(4):
            OTP += digits[math.floor(random.random() * 10)]

        # print(f"otp:::: {OTP}")

        return OTP

        # define the countdown func.

    def countdown(self, *args):
        """
        The countdown function is used to count down the time left for the user to enter their OTP.
        It starts at 30 seconds and counts down by 1 second until it reaches 0, then stops.

        :param self: Access variables that belongs to the class
        :param *args: Pass a variable number of arguments to a function
        :return: The value of self
        :doc-author: Trelent
        """

        # time.sleep(1)

        self.wm.get_screen("otp").ids['timer'].text = f"{str(self.t)} secs"
        self.t -= 1

        if self.t == 0:
            Clock.unschedule(self.countdown)
            otp = str(
                self.generate_otp())
            self.wm.get_screen("otp").ids['timer'].text = "0 secs"
            self.wm.get_screen("otp").ids['otp_lbl'].text = otp

            # self.t = 30
            self.notify.notify("OTP Expired")

    def expense_loader(self,  item, price, category):

        self.wm.get_screen('add_expense').ids['btn'].text = "Saving..."

        asynckivy.start(self.save_expense(item, price, category))

    def reset_btn_text_expense(self):
        self.wm.get_screen('add_expense').ids['btn'].text = "Save"

    async def save_expense(self, item, price, category, firebase=True):
        """
        The save_expense function saves the expense to the database.
        It takes in 3 parameters, item, price and category.
        The function checks if all fields are filled out before saving it to the database.
        If they are not filled out then an error message is displayed on screen.

        :param self: Access the attributes and methods of the class in python
        :param item: Store the item that is bought
        :param price: Store the price of the item bought
        :param category: Determine which category the expense belongs to
        :return: None
        :doc-author: Trelent
        """
        # try:
        email = self.wm.get_screen("login").ids['email'].text

        email = email.strip()
        email = email.lower()
        # except Exception:
        #     self.notify.notify("Unable to get email", error=True)

        if email == "" or item == "" or price == "":
            self.notify.notify("All fields must be filled", error=True)
            self.reset_btn_text_expense()
        elif price.replace(",", "").isdigit() == False:
            self.notify.notify(
                message="Only  (digits) allowed for price", error=True)
            self.reset_btn_text_expense()
        elif category == "choose category":
            self.notify.notify(message="Choose a category", error=True)
            self.reset_btn_text_expense()

        else:
            sql = "INSERT INTO expenses (email, item_bought, price, category_name, date) VALUES (?,?,?,?,?)"

            self.cursor.execute(
                sql, (email, item, price, category, today_date))

            self.conn.commit()
            self.wm.get_screen("add_expense").ids['price'].text = ""
            self.wm.get_screen("add_expense").ids['product'].text = ""
            self.wm.get_screen(
                "add_expense").ids['category'].text = "choose category"

            await asynckivy.run_in_thread(lambda: self.reset_btn_text_expense())

            self.notify.notify("expense updated successfully")
            self.wm.get_screen("home").ids['expense_container'].clear_widgets()

            await asynckivy.run_in_thread(lambda: self.fetch_expenses())

            # self.wm.get_screen(
            #     "home").ids['expense_container'].add_widget(ExpenseList(category=category.upper(), icon=icons[category.lower()], amount=price, date=str(today_date), item=item))

            await asynckivy.run_in_thread(lambda: self.calculate_expenses_and_percentage(if_login=True))

            # asynckivy.run_in_executer()

            # if self.amount_store.exists("total_expenses"):
            # total = self.amount_store.get("total_expenses")['total']
            # print(f"total1 :: {total}")
            # total2 = total + int(price.replace(",", ""))
            # print(f"total2 :: {total2}")
            # self.update_expense_after_save(total2)

            await asynckivy.run_in_thread(lambda: self.fetch_total_expenses_from_db())

            if firebase == True:
                await asynckivy.run_in_thread(lambda: FirebaseManager(
                ).add_expense(email, item, price, category, str(today_date)))

    def update_expense_after_save(self, total):
        """
        The update_expense_after_save function is called after the expense has been saved. 
        It takes in a total amount and updates the expenses_total label on the home screen.

        :param self: Access the instance of the class
        :param total: Update the total expenses on the home screen
        :return: The total expenses
        :doc-author: Trelent
        """

        self.amount_store.put("total_expenses", total=total)

        # self.manager.get_screen(
        # "home").ids['expense_container'].text =
        self.change_screen("home")

    def show_custom_bottom_sheet(self):
        self.custom_sheet = MDCustomBottomSheet(
            screen=UpdateBudgetContent(), radius_from="top", radius="30sp")
        self.custom_sheet.open()

    def update_dialog(self):
        """
        The update_dialog function creates a popup that allows the user to update their budget.
        It takes no parameters and returns nothing.

        :param self: Access the instance of the class
        :return: The instance of the update_popup
        :doc-author: Trelent
        """

        self.update_popup = Pop(title="Update Budget",
                                type="custom",
                                content_cls=UpdateBudgetContent(),)
        self.update_popup.open()

    def rewrite_dialog(self):
        """
        The rewrite_dialog function is called when the user clicks on a budget item in the list.
        It opens a popup window that allows them to update their budget.

        :param self: Refer to the current instance of a class
        :return: The popup
        :doc-author: Trelent
        """

        self.rewrite_popup = Pop(title="Update Budget",
                                 type="custom",
                                 content_cls=UpdateBudgetContent(),)
        self.rewrite_popup.open()

    def close(self, obj):
        self.update_popup.dismiss()

    def show_in_dialog(self, date, category_item, amount):
        """
        The show_in_dialog function is called when the user clicks on a row in the list.
        It takes three arguments: date, category_item, and amount. It then splits up the 
        category_item argument into two parts: category and item. The show_popup variable is set to an instance of Pop with title=item (the second part of category_item) and text = f&quot;category: {category}\ncost: {amount}\nDate:{date}&quot;. Finally, it opens this popup.

        :param self: Refer to the class itself
        :param date: Get the date of the expense
        :param category_item: Split the category and item into two separate variables
        :param amount: Show the amount of money spent on an item
        :return: The pop object
        :doc-author: Trelent
        """

        splitted = category_item.split(":")
        category = splitted[0]
        item = splitted[1]

        self.show_popup = Pop(title=item, text=f"category: {category.title()}\n"
                              f"cost: {amount}\n"
                              f"Date: {date}"

                              )
        self.show_popup.open()

    async def rewrite_budget(self, budget):

        email: str = self.wm.get_screen("login").ids['email'].text
        email = email.strip()
        email = email.lower()
        # old_budget = self.fetch_budget()
        # old_budget = old_budget.replace(
        #     ",", "") if "," in old_budget1 else old_budget1
        if budget == "":
            self.notify.notify(message="Enter your budget...", error=True)
        elif budget.replace(",", "").isdigit() == False:
            self.notify.notify(message="Only  (digits) allowed", error=True)
        else:
            # print(f"budget: {budget}")
            # print(f"old_budget: {old_budget}")
            new_budget = int(budget)
            sql = "UPDATE budget SET budget= ? WHERE email = ? AND date LIKE ? "
            self.cursor.execute(
                sql, (new_budget, email, f'%{self.month_year}%'))
            # print(f"em: l{email}l", self.month_year)
            # if run:
            # print(f"run {run}")
            self.conn.commit()
            # self.rewrite_popup.dismiss()
            await asynckivy.run_in_thread(lambda: self.calculate_expenses_and_percentage(if_login=False))
            self.update_popup.dismiss()
            self.notify.notify("Budget Updated")

            await asynckivy.run_in_thread(lambda:  self.firebase_manager.update_budget(email, new_budget, self.month_year))

    async def show_all_expenses(self, *args):
        """
        The show_all_expenses function is used to display all expenses in the database.
        It takes no arguments and returns nothing.

        :param self: Access the instance of a class
        :param *args: Pass a variable number of arguments to a function
        :return: All of the expenses in the database
        :doc-author: Trelent
        """

        # self.limit = 0
        await asynckivy.run_in_thread(lambda: self.fetch_expenses(limited=False))
        self.wm.get_screen("home").ids['spinner'].active = False

    def show_all_expenses_loader(self):
        """
        The show_all_expenses_loader function is used to load all expenses from the database and display them on the screen.
        It does this by clearing any widgets that are currently on the expense_container, then scheduling a function call to show_all_expenses after 2 seconds.


        :param self: Access the class attributes and methods
        :return: The expense_container widget of the home screen
        :doc-author: Trelent
        """

        self.wm.get_screen("home").ids['spinner'].active = True
        self.wm.get_screen("home").ids['expense_container'].clear_widgets()

        asynckivy.start(self.show_all_expenses())

    def change_screen(self, screen_name, switch=True, __from_goback=False):
        """
        The change_screen function changes the screen to a specified screen.
        It checks if the screen already exists in the ScreenManager, and if it does not exist,
        it creates a new instance of that class and adds it to the ScreenManager. It then changes
        the current screen to that specified.

        :param self: Access the attributes and methods of the class in python
        :param screen_name: Specify the screen that will be shown
        :param switch: Switch between screens
        :param __from_goback: Prevent the screen history from being updated when the user is going back to a previous screen
        :return: The screen manager object
        :doc-author: Trelent
        """

        # self.wm.current = screen_name
        # checks if the screen already exists in the screen manager
        # if the screen is not yet in the screen manager,
        if not self.wm.has_screen(screen_name):
            # gets the key screen name from the screens.json file
            getter = self.screens_store.get(screen_name)
            # executes the value of the import key in the screens.json file
            exec(getter['import'])

            # print(getter['object'])
            # print(getter['import'])
            # print(getter['kv'])

            # calls the screen class to get the instance of it
            screen_object = eval(getter["object"])
            # automatically sets the screen name using the arg that passed in set_current
            screen_object.name = screen_name
            # Builder.load_file(getter['kv'])
            # finnaly adds the screen to the screen-manager
            self.wm.add_widget(screen_object)
            # changes the screen to the specified screen
            # self.wm.current = screen_name
            # Builder.load_file(getter['kv'])

        # if the screens is already in the screen manager,
        # changes the screen to the specified screen
        if switch == True:
            self.wm.current = screen_name

        # if not __from_goback:
        if screen_name != "loader":
            self.screen_history.append({"name": screen_name, })

    def goback(self):
        """
        The goback function allows the user to go back one screen in the application.


        :param self: Access the class attributes
        :return: The previous screen
        :doc-author: Trelent
        """

        if len(self.screen_history) > 1:
            self.screen_history.pop()
            prev_screen = self.screen_history[-1]
            # print(self.screen_history)
            # print(prev_screen)

            self.change_screen(prev_screen["name"])

    def logout(self):
        """
        The logout function is used to logout of the application. It will change the screen back to login

        :param self: Access the class attributes
        :return: The screen name &quot;login&quot;
        :doc-author: Trelent
        """

        self.change_screen("login")

    def exit_popup(self):
        """
        The exit_popup function creates a popup window that asks the user if they want to exit the app.
        If yes, then it closes the app. If no, then it does nothing.

        :param self: Access the class attributes and methods
        :return: A pop object
        :doc-author: Trelent
        """
        self.exit_popup = None
        exit_btn = FlatButton(
            text="Exit", md_bg_color=self.warning, on_press=self.exit)
        cancel_btn = FlatButton(
            text="Go back", on_press=self.do_not_exit)
        self.exit_popup = Pop(title="Close app", text="Are you sure you want to exit app?", buttons=[
                              cancel_btn, exit_btn])

        self.exit_popup.open()

    def do_not_exit(self, *args):
        """
        The do_not_exit function is used to prevent the user from exiting out of a popup that has been
        opened by pressing the X button on the top right corner. This function is called when you press
        the &quot;Do not exit&quot; button in any popup.

        :param self: Access the attributes and methods of the class in python
        :param *args: Pass a variable number of arguments to a function
        :return: Nothing
        :doc-author: Trelent
        """

        self.exit_popup.dismiss()

    def exit(self, *args):
        """
        The exit function stops the program from running.

        :param self: Refer to the object that is calling the function
        :param *args: Pass a variable number of arguments to the function
        :return: The value none
        :doc-author: Trelent
        """

        self.stop()

    async def check_and_upload_to_firebase(self, *args):
        """
        The check_and_upload_to_firebase function checks if the user has signed up or saved a new expense they made.
        If they have, it will upload them.

        :param self: Access variables that belongs to the class
        :return: True if the data is uploaded to firebase
        :doc-author: Trelent
        """

        # from kvdroid.tools.network import network_status
        # if network_status():
        # print("check_if_signup()")
        signup_store = JsonStore(f"{self.path}/signup.json")
        if signup_store.count() > 0:
            # values = signup_store.get("values")
            for key in signup_store:
                store = signup_store.get(key)
                name = store["name"]
                email = store["email"]
                password = store["password"]

                await asynckivy.run_in_thread(lambda: self.firebase_manager.add_user(name=name, email=email, password=password))

        # print("check_if_expenses()")
        expense_store = JsonStore(f"{self.path}/expense1.json")
        if expense_store.count() > 0:
            # values = expense_store.get("values")
            for key in expense_store:
                store = expense_store.get(key)
                email = store["email"]
                item = store["item"]
                price = store["price"]
                category = store["category"]
                date = store["date"]
            # print(email, item, category, price, category)
            await asynckivy.run_in_thread(lambda: self.firebase_manager.add_expense(email, item, price, category, date))

        # print("check_if_budget()")
        budget_store = JsonStore(f"{self.path}/budget.json")
        if budget_store.count() > 0:
            # values = expense_store.get("values")
            for key in budget_store:
                store = budget_store.get(key)
                email = store["email"]
                budget = store["budget"]
                date = store["date"]
            # print(email, budget, date)
            await asynckivy.run_in_thread(lambda: self.firebase_manager.add_budget(email, budget,  date))

        # print("check_if_budgetupdate()")
        budget_update_store = JsonStore(f"{self.path}/budget_update.json")
        if budget_update_store.count() > 0:
            # values = expense_store.get("values")
            for key in budget_update_store:
                store = budget_update_store.get(key)
                email = store["email"]
                budget = store["budget"]
                date = store["month_year"]
            # print(email, budget, date)
            await asynckivy.run_in_thread(lambda: self.firebase_manager.update_budget(email, budget,  date))

        # print("check_if_paswordupdate()")
        password_update_store = JsonStore(f"{self.path}/password_update.json")
        if password_update_store.count() > 0:
            # values = expense_store.get("values")
            for key in password_update_store:
                store = password_update_store.get(key)
                email = store["email"]
                password = store["password"]

            # print(email, budget, date)
            await asynckivy.run_in_thread(lambda: self.firebase_manager.update_password(email, password))

    def get_theme(self):
        """
        The get_theme function returns the current theme as a string.


        :param self: Represent the instance of the class
        :return: The current theme
        :doc-author: Trelent
        """
        theme = self.theme_store.get('theme')['current_theme']
        return theme

    def put_theme(self, theme):
        """
        The put_theme function changes the theme of the app.
            Args:
                theme (str): The name of the new theme to be applied.


        :param self: Represent the instance of the class
        :param theme: Change the theme of the application
        :return: Nothing
        :doc-author: Trelent
        """

        self.theme_store.put("theme", current_theme=theme)
        #print(f"change theme to {theme}")

        # self.change_theme(theme)

    def switch_theme_style(self, change_theme: bool = True):
        """
        The switch_theme_style function is used to switch the theme style of the app.
        It also changes some colors that are not affected by changing the theme_style, such as
        the primary and secondary colors. It does this by checking if it's a light or dark theme,
        and then setting all of these values accordingly.

        :param self: Represent the instance of the class
        :param change_theme: bool: Determine whether the theme should be changed or not
        :return: A dictionary
        :doc-author: Trelent
        """

        # self.theme_cls.primary_palette = (
        #     "Orange" if self.theme_cls.primary_palette == "Blue" else "Blue"
        # )
        if change_theme == True:
            if self.get_theme() == "light":
                self.put_theme("dark")
            else:
                self.put_theme("light")

        # self.theme_cls.theme_style = (
        #     "Light" if self.theme_cls.theme_style == "Dark" else "Dark"
        # )

        self.theme_cls.theme_style = self.get_theme().title()

        self.primary = rgba(
            "#143EBE") if self.theme_cls.theme_style == "Light" else rgba('#071B63')

        self.secondary = self.theme_cls.primary_color if self.theme_cls.theme_style == "Light" else self.theme_cls.accent_dark
        # self.secondary = hex_colormap['purple'] if self.theme_cls.theme_style == "Light" else rgba(
        #     "#070C10")

        self.bg = rgba(
            "#FFFFFF") if self.theme_cls.theme_style == "Light" else rgba('#19181A')
        # print(f"bg: {self.bg}")

        self.text_color = rgba(
            "#FFFFFF") if self.theme_cls.theme_style == "Dark" else rgba("#19181A")
        # print(f"text_color: {self.text_color}")

        self.icon_color = rgba(
            "#FFFFFF") if self.theme_cls.theme_style == "Dark" else rgba("#FFFFFF")
        # print(f"icon_color: {self.icon_color}")

        self.card_color = rgba(
            "#19181a") if self.theme_cls.theme_style == "Dark" else rgba("#FFFFFF")
        # print(f"card_color: {self.card_color}")

        self.fill_color = rgba(
            '#f1f1f1') if self.theme_cls.theme_style == "Dark" else rgba('#FFFFFF')
        # print(f"fill_color: {self.fill_color}")

        self.textfield_text = rgba(
            '#19181A') if self.theme_cls.theme_style == "Dark" else rgba('#19181A')
        # print(f"textfield_text: {self.textfield_text}")

        self.warning = rgba(
            '#Ff8c00') if self.theme_cls.theme_style == "Dark" else rgba('#B90000')
        # print(f"warning: {self.warning}")

        self.danger = rgba(
            '#FF6F00') if self.theme_cls.theme_style == "Dark" else rgba('#B90000')
        # print(f"danger: {self.danger}")

        self.orange = rgba(
            '#ed8a0a') if self.theme_cls.theme_style == "Dark" else rgba('#ed8A0A')
        # print(f"orange: {self.orange}")

        self.yellow = rgba(
            '#f6d912') if self.theme_cls.theme_style == "Dark" else rgba('#f6d912')
        # print(f"yellow: {self.yellow}")

        self.white = rgba(
            '#ffffff') if self.theme_cls.theme_style == "Dark" else rgba('#ffffff')
        self.white = rgba(
            '#ffffff') if self.theme_cls.theme_style == "Dark" else rgba('#ffffff')
        self.grey = rgba(
            '#ffffff') if self.theme_cls.theme_style == "Dark" else rgba('#ececec')
        self.grey2 = rgba(
            '#A9a9a9') if self.theme_cls.theme_style == "Dark" else rgba('#8a8a8a')
        self.black = rgba(
            '#333333') if self.theme_cls.theme_style == "Dark" else rgba('#333333')
        self.success = rgba(
            "#154734")if self.theme_cls.theme_style == "Dark" else hex_colormap['darkolivegreen']

    @staticmethod
    def start_service():
        """
        The start_service function starts the MoneyWatch service.


        :return: A service object
        :doc-author: Trelent
        """

        if platform == "android":
            from jnius import autoclass
            service = autoclass("org.humfadh.moneywatcher.ServiceMoneywatcher")
            # SERVICE_NAME = u'{packagename}.Service{servicename}'.format(
            # packagename=u'org.kivy.test',
            # servicename=u'Myservice')
            # service = autoclass(SERVICE_NAME)
            mActivity = autoclass('org.kivy.android.PythonActivity').mActivity
            argument = ''
            service.start(mActivity, argument)
            return service
