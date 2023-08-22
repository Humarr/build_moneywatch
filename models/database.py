# from __future__ import annotations

# import socket
import sqlite3

# import plyer

# import requests

# from pyrebase import pyrebase

from utils.androidly import Storage
from models.firebase_db import FirebaseManager
from widgets.notify import Notify
from kivy.clock import Clock
import asynckivy


class DatabaseManager:
    """
    Your methods for working with the database should be implemented in this
    class.
    """
    __instance = None

    # @staticmethod
    # def get_instance():
    #     if DatabaseManager.__instance is None:
    #         DatabaseManager()
    #     return DatabaseManager.__instance

    def __init__(self):
        # if DatabaseManager.__instance is not None:
        #     pass
        # else:
        # try:
        self.integrity_error = sqlite3.IntegrityError
        self.operational_error = sqlite3.OperationalError
        self.path = Storage().storage()

        if self.path:

            self.conn = sqlite3.connect(f"{self.path}/money.db", check_same_thread=False)

            self.cursor = self.conn.cursor()
                # self.__class__.__instance = self
        #     else:
        #         print("Not connecting database")
        # except sqlite3.DatabaseError() as e:
            

    def execute(self, query):
        self.get_instance().cursor.execute(query)
        return self.cursor.fetchall()

    def create_user_account(self, name, email, password):
        """
        The create_account function is used to create a new account for the user.
        It takes in three parameters: name, email and password. The function then uses an SQL query to insert these values into the database table called 'user_info'.
        The function also calls on another function called notify which displays a message on screen telling the user that their account has been created successfully. 
        The current screen is then changed from signup to login using self.manager and finally, we commit our changes to the database.

        :param self: Represent the instance of the class
        :param name: Get the name of the user
        :param email: Store the email address of the user
        :param password: Store the password of the user
        :return: A clock
        :doc-author: Trelent
        """

        try:

            email = email.strip()
            sql = "INSERT INTO user_info (username, email,  password) VALUES (?, ?, ?)"
            self.cursor.execute(sql, (name.lower(), email.lower(), password,))
            Notify().notify("Account created successfully")
            self.manager.current = "login"
            self.conn.commit()
            self.reset_btn_text_signup()


            # Clock.schedule_once(
            #     lambda x: FirebaseManager().add_user(name, email, password), 2)

            # lambda x: FirebaseManager().add_user(
            #     name, email, password)

        except sqlite3.IntegrityError:
            self.reset_btn_text_signup()

            Notify().notify("Email already registered", error=True)

    def build_tables(self):
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS user_info (user_id INTEGER PRIMARY KEY AUTOINCREMENT, username VARCHAR(255) NOT NULL, email VARCHAR(255) NOT NULL UNIQUE, password VARCHAR(25) NOT NULL)")

        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS budget (budget_id INTEGER PRIMARY KEY AUTOINCREMENT,email VARCHAR(255), budget INT NOT NULL, date DATE)")

        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS categories (category_id INTEGER PRIMARY KEY AUTOINCREMENT, category_name VARCHAR(255))")

        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS expenses(id INTEGER PRIMARY KEY AUTOINCREMENT, email VARCHAR(255), item_bought VARCHAR(255), price VARCHAR(255), category_name VARCHAR(255), date DATE)")

        # month = '2023-04'
        # self.cursor.execute("UPDATE  expenses SET category_name = ? WHERE email=? AND date LIKE ?", ( "Security", "h@m.com", f'%{month}%'))
        # self.cursor.execute("UPDATE  budget SET budget = ? WHERE email=? AND date LIKE ?", ( "560000", "h@m.com", f'%{month}%'))
        # self.cursor.execute("UPDATE  expenses SET item_bought = ? WHERE item_bought=? AND date LIKE '%2023-03%'", ("canva course (benji)", "Canva course(Benji)"))
        # self.cursor.execute("DROP table budget")
        # self.cursor.execute("DROP table expenses")
        self.conn.commit()

    def fetch_tables(self):
        sql = "SELECT * FROM budget WHERE email=?"
        # sql = "SELECT * FROM budget WHERE email=? AND strftime('%Y-%m', budget) =?"
        self.cursor.execute(sql, ("h@m.com", ))
        # self.cursor.execute(sql, (email,))
        # global result
        result = self.cursor.fetchall()

        print(f"budget_result: {result}")


DatabaseManager().build_tables()
# DatabaseManager().fetch_tables()


#
