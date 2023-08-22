from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from kivymd.uix.behaviors import CommonElevationBehavior
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.list import ThreeLineAvatarListItem
from kivy.properties import StringProperty
from models.database import DatabaseManager
from widgets.notify import Notify
from utils.today import date_dict2, today_date
from kivy.clock import Clock, mainthread
from utils.popup_items import icons
import asynckivy


class ExpenseList2(MDFloatLayout, CommonElevationBehavior, ThreeLineAvatarListItem):
    category: str = StringProperty()
    icon: str = StringProperty("food")
    amount: str = StringProperty()
    date: str = StringProperty()
    item: str = StringProperty()


Builder.load_file("views/expenses.kv")


"""
The ExpensesScreen class is responsible for displaying and searching for expenses in the database. It provides methods to search for expenses based on a given search term, fetch expenses from the database, and clear the current expenses displayed on the screen. The class also includes a method to update the text of a widget based on user input.

Methods:
- search(search: str, *args): Searches for expenses in the database based on a given search term. If found, it displays the expenses on the screen.
- get_expenses_from_database(month_year): Fetches expenses from the database for a specific month and year and adds them to the expense_container widget.
- on_typing(search_text): Updates the text of the date_expense widget based on user input.
- expenses_search_loader(search): Loads the search function and clears the current expenses displayed on the screen.
- clear_current_expenses(*args): Clears the expense_container widget of all expenses.

Fields:
- cursor: An instance of the cursor class from the DatabaseManager class.

Author: Trelent
"""
class ExpensesScreen(MDScreen):
    cursor = DatabaseManager().cursor

    async def search(self, search: str, *args):
        """
        The search function is used to search for expenses in the database.
        It takes a string as an argument and searches through the database for that string.
        If found, it displays all the expenses with that particular string in them.

        :param self: Access variables that belongs to the class
        :param search: Search for the expense of a particular month
        :return: A list of widgets that have been added to the expense_container
        :doc-author: Trelent
        """

        """Fetches all the amount spent for the month from the database"""
        
        if search == "":
            Notify().notify("Enter a search term...", error=True)
            self.ids['spinner'].active = False

        elif  ',' not in search:
            self.ids['spinner'].active = False
            Notify().notify("must be in the form:: Month, Year", error=True)

        else:
            search = search.strip()
            search = search.replace(" ", "")

            search = search.split(",")

            keys = date_dict2.keys()

            for key in keys:
                if key in search[0].title():
                    # break
                    month = date_dict2.get(search[0][:3].title())
                    year = search[1]

                    month_year = f"{year}-{month}"

                    await asynckivy.run_in_thread(lambda: self.get_expenses_from_database(month_year))
                    break
            else:
                Notify().notify("Enter a correct month", error=True)
                self.ids['spinner'].active = False



    @mainthread
    def get_expenses_from_database(self, month_year):
        try:
            email = self.manager.get_screen("login").ids['email'].text
            email = email.strip()
            email = email.lower()
            sql = "SELECT * FROM expenses WHERE email=? AND date LIKE ?"
            self.cursor.execute(sql, (email, f'%{month_year}%',))
            result = self.cursor.fetchall()


            if result:
                for value in result:

                    price = value[3]
                    item = value[2]
                    date = value[5]
                    icon = value[4].lower()
                    category = value[4].upper()

                    self.ids['expense_container'].add_widget(ExpenseList2(
                        category=category, icon=icons[icon], amount=price, date=date, item=item))
                # break
                self.ids['spinner'].active = False
            else:
                Notify().notify("No expenses in the specified month", error=True)

                self.ids['spinner'].active = False

            # break
        except IndexError:
            Notify().notify("the month and year should be separated by ','", error=True)

            self.ids['spinner'].active = False

    def on_typing(self, search_text):
        """
        The on_typing function is called when the user types in the search bar. 
        It takes a single argument, which is the text that was entered into the search bar. 
        The function then sets self.ids['date_expense'] to be equal to f&quot;Expenses For {search_text}&quot;. 

        :param self: Access the attributes and methods of the class in python
        :param search_text: Set the text of the date_expense widget
        :return: The text of the date_expense widget
        :doc-author: Trelent
        """

        self.ids['date_expense'].text = f"Expenses For {search_text.title()}"

    def expenses_search_loader(self, search):
        self.ids['spinner'].active = True
        Clock.schedule_once(self.clear_current_expenses)
        asynckivy.start(self.search(search))

    def clear_current_expenses(self, *args):
        """
        The clear_current_expenses function clears the expense_container widget of all widgets.


        :param self: Access the attributes and methods of the class in python
        :param *args: Pass a variable number of arguments to a function
        :return: The expense_container widget
        :doc-author: Trelent
        """

        self.ids['expense_container'].clear_widgets()