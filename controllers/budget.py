from time import sleep
from kivymd.uix.screen import MDScreen
from kivy.lang import Builder

from models.database import DatabaseManager

from kivy.clock import Clock
from models.firebase_db import FirebaseManager
from utils.today import today_date
import asynckivy
from widgets import notify
from widgets.popup import Pop


Builder.load_file("views/budget.kv")


class BudgetScreen(MDScreen):

    conn = DatabaseManager().conn

    cursor = conn.cursor()

    def format(self, budget):
        """
        The format function takes a number and inserts commas into it to make it more readable.
        For example, if you give format function the parameter 3145 it will return 3,145.

        :param self: Access variables that belongs to the class
        :param budget: Format the budget value to a more readable format
        :return: A formatted string from the input
        :doc-author: Trelent
        """
        try:

            if len(budget) > 3:
                budget = budget.replace(",", "")
                formatted_budget = (format(int(budget),  ',d'))

                self.ids['budget'].text = formatted_budget

        except ValueError:
            notify.Notify().notify(message="The budget must be a digit")

    async def save_budget(self, budget, *args):
        """
        The save_budget function saves the budget entered by the user to a database.
        It takes in one argument, budget and returns nothing.

        :param self: Access variables that belongs to the class
        :param budget: Store the budget entered by the user
        :return: None
        :doc-author: Trelent
        """

        email = self.manager.get_screen("login").ids['email'].text
        email = email.strip()
        email = email.lower()

        if budget == "":
            notify.Notify().notify("Enter your month's budget", error=True)
        elif budget.replace(",", "").isdigit() == False:
            notify.Notify().notify(message="Only  (digits) allowed", error=True)
        else:
            sql = "INSERT INTO budget (email, budget, date) VALUES (?,?,?)"
            self.cursor.execute(sql, (email, budget, today_date))
            self.conn.commit()
            notify.Notify().notify("budget updated successfully")

            self.manager.current = "login"
            self.popup = Pop(
                text="Please, Login Again for everything to load properly")

            self.popup.open()

            await asynckivy.run_in_thread(lambda: FirebaseManager().add_budget(
                email, budget, str(today_date)))

    def budget_loader(self, budget):
        self.ids['btn'].text = "Saving Budget..."
        asynckivy.start(self.save_budget(budget))

    def budget_btn_reset(self, budget, *args):
        self.ids['btn'].text = "Save Budget"
