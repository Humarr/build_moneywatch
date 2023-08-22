from time import sleep
from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from controllers.home import ExpenseList
from utils.androidly import Storage
from models.database import DatabaseManager
from utils.today import today_date
from utils.popup_items import items, icons
from widgets import notify
from widgets.button import FlatButton
from widgets.popup import Pop
from kivymd.uix.list import OneLineIconListItem
from kivy.properties import StringProperty
from kivy.clock import Clock
from kivy.storage.jsonstore import JsonStore


class Items(OneLineIconListItem):
    """
    A class representing a list item with an icon and a text label.

    This class is a subclass of the 'OneLineIconListItem' class from the KivyMD library.
    It provides a template for creating list items that can be used in pop-ups or other widgets.

    Attributes:
        text (str): The text of the list item.
        icon (str): The icon of the list item.
    """

    text = StringProperty()
    icon = StringProperty()

    def on_press(self):
        """
        Called when the list item is pressed.
        """
        pass

    def on_release(self):
        """
        Called when the list item is released.
        """
        pass


Builder.load_file("views/add_expense.kv")


"""
This class represents the screen where users can add new expenses to their budget. It provides functionality for formatting the input of the user, loading and displaying categories, and adding new expenses to the database.

Methods:
- format(expense): Formats the input expense by adding comma separators to the number.
- categories_loader(): Loads the categories from the 'items' dictionary and displays them in a popup.
- categories(): Creates a list of items that can be selected from and displays them in a popup.
- show_category_in_field(instance): Sets the text of the category field to the selected category.
- show(instance): Sets the text of the category field to the selected category and closes the categories popup.
- dis(obj): Closes the categories popup.
- close_categories_list(): Closes the categories popup.

Fields:
- db: An instance of the 'DatabaseManager' class.
- conn: A connection to the database.
- cursor: A cursor for executing SQL queries.
- path: The path to the storage folder where data files are saved.
- amount: A JsonStore object for storing the amount of the expense.
- current: The current date.
- month_year: The current month and year.
"""
class AddExpenseScreen(MDScreen):

    db = DatabaseManager()
    conn = db.conn
    cursor = conn.cursor()

    path = Storage().storage()
    amount = JsonStore(f"{path}/expenses.json")
    current = str(today_date).split("-")
    month_year = f"{current[0]}-{current[1]}"

    def format(self, expense):
        """
        The format function takes a number (expense) as an argument and returns it with comma separators.
        For example: format(123456789, ',') will return 1,234,56789

        :param self: Access variables that belongs to the class
        :param expense: Store the value of expense that is entered by the user
        :return: The formatted string of the input number
        :doc-author: Trelent
        """

        try:
            if len(expense) > 3:
                expense = expense.replace(",", "")
                formatted_expense = (format(int(expense),  ',d'))

                self.ids['price'].text = formatted_expense
        except ValueError:
            notify.Notify().notify(message="The price must be a digit")

    def categories_loader(self, *instance):
        self.ids['category'].text = "Loading Categories..."
        Clock.schedule_once(lambda x: self.categories(instance), 2)

    def categories(self, *instance):
        """
        The categories function creates a list of items that can be selected from.
        The items are displayed in a popup and when an item is selected, the function
        returns the text of the item. This text is then used to update the category field.

        :param self: Access variables that belongs to the class
        :param *instance: Pass the instance of the widget that called this function
        :return: A list of items that are assigned to the categories
        :doc-author: Trelent
        """

        items_list = []

        for icon, category in items.items():
            items_list.append(
                Items(text=category, icon=icon, on_press=self.show_category_in_field))

        self.categories_pop = Pop(title="Categories...",
                                  type="simple",
                                  items=items_list,

                                  )
        self.categories_pop.open()
        self.ids['category'].text = "choose category"

    def show_category_in_field(self, instance):
        """
        The show_category_in_field function is used to set the text of the category field to whatever was selected in the categories_popup.


        :param self: Access the attributes and methods of the class
        :param instance: Get the text from the button that was clicked
        :return: The category that was selected in the categories_popup
        :doc-author: Trelent
        """

        self.categories_pop.dismiss(force=True)

        Clock.schedule_once(lambda x: self.show(instance))

    def show(self, instance):
        """
        The show function is called when a user clicks on one of the buttons in the categories_pop pop-up.
        The show function takes an instance as its argument, which is passed to it by Kivy's bind() method.
        The instance variable contains information about the button that was clicked, including its text property. 
        This text property is used to set the category label's text attribute.

        :param self: Represent the instance of the class
        :param instance: Get the text from the button that was clicked
        :return: The text of the category selected
        :doc-author: Trelent
        """

        self.ids['category'].text = instance.text.title()
        self.categories_pop.dismiss(force=True)

    def dis(self, obj):
        # print(obj)
        self.categories_pop.dismiss(force=True)

    def close_categories_list(self, *args):
        """
        The close_categories_list function closes the categories list when called.


        :param self: Access the attributes and methods of the class in python
        :param *args: Pass a variable number of arguments to a function
        :return: The categories_pop
        :doc-author: Trelent
        """

        self.categories_pop.dismiss(force=True)
