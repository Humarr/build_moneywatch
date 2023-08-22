from kivy.storage.jsonstore import JsonStore
# from requests.packages.urllib3.contrib import appengine
from pyrebaser import pyrebaser
# from requests.packages.urllib3.contrib.appengine import is_appengine_sandbox
from utils.androidly import Storage
# from urllib3.contrib.appengine import is_appengine_sandbox
# from widgets.notify import Notify
# from kvdroid.tools.path import sdcard
#

config = {
    'apiKey': "AIzaSyAApNPZ3UXPnr8tX090xiCf8WmMAXCbkm4",
    'authDomain': "moneywatcher1.firebaseapp.com",
    'databaseURL': "https://moneywatcher1-default-rtdb.asia-southeast1.firebasedatabase.app",
    'projectId': "moneywatcher1",
    'storageBucket': "moneywatcher1.appspot.com",
    'messagingSenderId': "342556134968",
    'appId': "1:342556134968:web:afd9a5f520f152d414a0cd",
    'measurementId': "G-37FP9VHDGN"
}

firebase = pyrebaser.initialize_app(config)


class FirebaseManager:
    def __init__(self):
        """
        The __init__ function is called the constructor and is automatically called when you create a new object.
        The primary purpose of this function is to initialize all variables that are owned by the specific instance of a class.

        :param self: Refer to the object itself
        :return: The auth, database and storage objects
        :doc-author: Trelent
        """

        self.auth = firebase.auth()
        self.db = firebase.database()
        self.storage = firebase.storage()
        # self.path = sdcard()
        self.path = Storage().storage()

    def firebase_database_login(self, email, password):
        """
        The firebase_database_login function logs into the firebase database and returns a user object. 
        The function takes two arguments, email and password, which are used to log in to the database.

        :param self: Reference the class itself
        :param email: Store the email address of the user
        :param password: Authenticate the user
        :return: A dictionary containing the user's authentication token
        :doc-author: Trelent
        """

        try:
            self.auth.sign_in_with_email_and_password(email, password)
        except Exception as e:
            print(f"singin error: {e}")

    def firebase_database_signup(self, email, password):
        """
        The firebase_database_signup function creates a new user in the Firebase database.
        It takes two arguments, email and password, which are both strings.

        :param self: Access the variables and methods of the class in python
        :param email: Store the email of the user
        :param password: Set the password of the user
        :return: A json object containing the user's unique id and auth token
        :doc-author: Trelent
        """

        try:
            self.auth.create_user_with_email_and_password(email, password)
        except Exception as e:
            print(f"singup error: {e}")

    def add_user(self, name, email, password):
        """
        The add_user function adds a user to the database.
        It takes three parameters: name, email and password.


        :param self: Access the class attributes and methods
        :param name: Store the name of the user
        :param email: Check if the email already exists in the database
        :param password: Encrypt the password
        :return: None
        :doc-author: Trelent
        """

        data = {
            "name": name,
            "email": email,
            "password": password
        }
        signup_store = JsonStore(f"{self.path}/signup.json")
        try:
            res = self.db.child("users").get()
            # print(f"res: {res.val()}")
            # print(f"res: {res.key()}")
            for user in res.each():
                # print(user.val())
                if user.val()['email'] == email:
                    # Notify().notify("Email already exists", error=True)
                    break
            else:
                email_header = email.replace(".", "-")
                self.db.child("users").child(email_header).set(data)

                if signup_store.exists(email):
                    signup_store.delete(email)
        except (ConnectionAbortedError, ConnectionError, ConnectionRefusedError, ConnectionResetError, Exception) as e:
            print(e)

            signup_store.put(email, name=name,
                             email=email, password=password, )
            # Notify().notify("No or Weak network connection", error=True)

    def fetch_user(self, email, password):
        try:
            res = self.db.child("users").get()
            # print(f"resval: {res.val()}")
            # print(f"reskey: {res.key()}")
            for user in res.each():
                # print(f"userval: {user.val()}")
                # print(f"uservalemail: {user.val()['email']}")
                if email== user.val()['email']   and password == user.val()['password']:
                    name = user.val()['name']
                    # print(f"name: {name}")
                    # break
                    return [email, password]
            else:
                print("fetched nothing")
        except  (ConnectionAbortedError, ConnectionError, ConnectionRefusedError, ConnectionResetError, Exception) as e:
            print(e)
    def fetch_expenses(self, email):
        try:
            email = email.replace(".", "-")
            res = self.db.child("expenses").get()
            # res = self.db.child("expenses").child(email).get()
            # print(f"resval: {res.val()}")
            # print(f"reskey: {res.key()}")
            # print(f"reseach: {res.each()}")

            for expense in res.each():
                # print(f"expenseval: {expense.val()}")
                # print(f"expenseval email: {expense.val()['email']}")
                for value in expense.val():
                    
                    email_gotten = expense.val()[value]['email']
                    # print(f"email gotten: {email_gotten}")
                    if email_gotten == email:
                        pass
                        # print("gotcha")
                    # if value.val()['email'] == email:
                    #     print(f"email found for expense")
                        # for value in expense.val()['email']:
                        #     print(value)
                    
                # print(f"uservalemail: {user.val()['email']}")

                # email = expense.val()['email']
                # item = expense.val()['item']
                # price = expense.val()['price']
                # category = expense.val()['category']
                # # name = user.val()['name']
                # print(f"name: {name}")
                # break
                # return res.each()
            # else:
            #     print("fetched nothing")
        except  (ConnectionAbortedError, ConnectionError, ConnectionRefusedError, ConnectionResetError, Exception) as e:
            print(e)

    def add_expense(self, email, item, price, category, date):
        """
    The add_expense function adds an expense to the database.
        Args:\n
            email (str): The email of the user who added the expense.\n
            item (str): The name of the item that was purchased.\n
            price (float): The cost of the item in USD.  For example, if you bought a  gift card for .50, this would be 5 and price would be 3.50).

    :param self: Access the class attributes and methods
    :param email: Store the email of the user
    :param item: Store the item name
    :param price: Store the price of the item
    :param category: Determine which category the expense will be added to
    :return: None
    :doc-author: Trelent
    """

        data = {
            "email": email,
            "item": item,
            "price": price,
            "category": category,
            "date": date
        }
        expense_store = JsonStore(f"{self.path}/expense1.json")
        try:
            email = email.replace('.', '-')

            # self.db.child("expenses").push(data)

            self.db.child("expenses").child(email).push(data)
            # self.db.child("expenses").push(data)
            if expense_store.exists(item):
                expense_store.delete(item)
        except (ConnectionAbortedError, ConnectionError, ConnectionRefusedError, ConnectionResetError, Exception) as e:
            print(e)
            day = str(date)

            expense_store.put(item, email=email, item=item,
                              price=price, category=category, date=day)
            # Notify().notify("No or Weak network connection", error=True)

    def remove_expense(self,email, amount, category, date):
        delete_store = JsonStore(f"{self.path}/deleted.json")
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
        # email = self.wm.get_screen("login").ids['email'].text
        email = email.strip()

        try:
            # email = email.replace(".", "-")
            res = self.db.child("expenses").get()

            price_list = []

            for expense in res.each():
                # print(f"expenseval: {expense.val()}")

                for value in expense.val():

                    if expense.val()[value]['email'].replace("-", ".") == email and date == expense.val()[value]['date'] and amount == expense.val()[value]['price'] and item == expense.val()[value]['item']:
                        # print(
                            # f" the email: {expense.val()[value]['email']}")
                        # print(f"normal: {email}")

                        # email = expense.val()[value]['email']
                        # email = email.replace("-", ".")
                        # print("expenses loading...")

                        email = email.replace(".", "-")
                        # self.db.child("expenses").child(email).remove()
                        self.db.child("expenses").child(email).child(value).remove()
                        delete_store.delete(item)
                        break
        except (ConnectionAbortedError, ConnectionError, ConnectionRefusedError, ConnectionResetError, Exception) as e:
            print(e)
            delete_store.put(item, email=email, item=item,
                              price=amount, category=category, date=date)

            # expense_store.put(item, email=email, item=item,
            #                   price=price, category=category, date=day)
            # Notify().notify("No or Weak network connection", error=True)

    def add_budget(self,email, budget, date):
        data = {
            "email": email,
            "budget": budget,
            "date": date
        }
        budget_store = JsonStore(f"{self.path}/budget.json")
        # budget_store = JsonStore("budget.json")
        try:
            emails = email.replace('.', '-')

            # self.db.child("expenses").push(data)
                                        # date = expense.val()[value]['date']
            self.db.child("budgets").child(emails).push(data)
            if budget_store.exists(str(date)):
                budget_store.delete(str(date))
        except (ConnectionAbortedError, ConnectionError, ConnectionRefusedError, ConnectionResetError, Exception) as e:
            print(f"budget: {e}")
            date = str(date)

            budget_store.put(str(date), email=email, budget=budget, date=date)
            # Notify().notify("No or Weak network connection", error=True)
    
    def update_budget(self,email, new_budget, month_year):
        budget_update_store = JsonStore(f"{self.path}/budget_update.json")
        try:
            res = self.db.child("budgets").get()
            # print(f"resval: {res.val()}")
            # print(f"reskey: {res.key()}")
            update_values = {
                "budget": new_budget
            }
            for values in res.each():
                #     print(f"budgetval: {values.val()}")
                # print(self.month_year)
                # print(f"uservalemail: {user.val()['email']}")
                for value in values.val():

                    budget = values.val()[value]['budget']
                    date = values.val()[value]['date']
                    emails = values.val()[value]['email']
                    
                    # print(f"budget: {budget}")
                    # print(f"date: {date}")
                    # print(f"email: {email}")

                # email = values.val()['email']
                    if email == emails.replace("-", ".") and month_year in date:
                        self.db.child("budgets").child(email.replace(".","-")).child(value).update(update_values)

                        if budget_update_store.exists(month_year):
                            budget_update_store.delete(month_year)
        except (ConnectionAbortedError, ConnectionError, ConnectionRefusedError, ConnectionResetError, Exception) as e:
            print(f"budget: {e}")
            # date = str(date)

            budget_update_store.put(month_year, email=email, budget=new_budget, month_year=month_year)

    def update_password(self,email, new_password):
        password_update_store = JsonStore(f"{self.path}/password_update.json")
        try:
            res = self.db.child("users").get()
            # print(f"resval: {res.val()}")
            # print(f"reskey: {res.key()}")
            update_values = {
                "password": new_password
            }
            for values in res.each():
                #     print(f"budgetval: {values.val()}")
                # print(self.month_year)
                # print(f"uservalemail: {user.val()['email']}")
                # for value in values.val():

                emails = values.val()['email']
                password = values.val()['password']
                name = values.val()['name']
                
                # print(f"email: {emails}")
                # print(f"password: {password}")
                # print(f"name: {name}")

            # email = values.val()['email']
                if email == emails:
                    self.db.child("users").child(email.replace(".","-")).update(update_values)

                    if password_update_store.exists(email):
                        password_update_store.delete(email)
        except (ConnectionAbortedError, ConnectionError, ConnectionRefusedError, ConnectionResetError, Exception) as e:
            print(f"password update: {e}")
            # date = str(date)

            password_update_store.put(email, email=email, password=new_password)
# FirebaseManager().add_user("umar", "emailer@email.com", "12345")
# print(FirebaseManager().fetch_user("humarr@gmail.com", "Qwerty1#"))
# FirebaseManager().fetch_expenses("m@g.com")
# FirebaseManager().fetch_expenses("sal@yahoo.edu")
# FirebaseManager().add_expense("sal@yahoo.edu", "item", "2000", "category", "2023-02-02")
# FirebaseManager().add_budget("m@g.com", "40,000", "2023-09-12")
# FirebaseManager().fetch_user("humarr@gmail.com", "Qwerty1#"
# FirebaseManager().fetch_user("humarr@gmail.com", "Qwerty1#"
# FirebaseManager().remove_expense("h@m.com","2,000", "Education: prod", "2023-04-23")
# FirebaseManager().update_budget("h@m.com", "40,000", "2023-04")
# FirebaseManager().update_password("h@m.com", "Qwerty1@")