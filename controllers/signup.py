import sqlite3
from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
import re
from models.database import DatabaseManager
from kivy.clock import Clock
from models.firebase_db import FirebaseManager
from utils.validation import validate_email, validate_password
from widgets import notify
import asynckivy


Builder.load_file("views/signup.kv")


class SignupScreen(MDScreen):
    # def __init__(self):

    db = DatabaseManager()
    conn = db.conn
    cursor = conn.cursor()

    def signup(self, name, email, password):
        """
        The signup function is used to create a new user account. It takes in the name, email and password of the user as parameters.
        It then checks if the email address is valid and if it's not, it displays an error message on screen. If it's valid, 
        it checks if there are any other accounts registered with that same email address already present in our database by querying our database for all emails currently stored within our system. If no such emails are found, we proceed to insert this new account into our database along with its corresponding username and password.

        :param self: Access variables that belong to the class
        :param name: Set the username
        :param email: Validate the email address
        :param password: Validate the password entered by the user
        :return: The email and password validated
        :doc-author: Trelent
        """

        if not validate_email(email):
            email_validated = email

            notify.Notify().notify("Please enter a valid email address", error=True)
            self.reset_btn_text_signup()

        elif not validate_password(password):
            password_validated = password
            notify.Notify().notify(
                "Password must: be at least 6 characters, have a digit, letter, uppercase letter and a symbol", "dialog")
            self.reset_btn_text_signup()

        else:
            asynckivy.start(self.create_user_account(name, email, password))

    def signup_loader(self, name, email, password):
        """
        The signup_loader function is called when the user clicks on the signup button. 
        It takes in 3 parameters: name, email and password. It then calls the signup function with these parameters.

        :param self: Access the attributes and methods of the class in python
        :param name: Store the name of the user
        :param email: Store the email address entered by the user
        :param password: Store the password entered by the user
        :return: The value of the signup function
        :doc-author: Trelent
        """

        self.ids['btn'].text = "Saving..."

        Clock.schedule_once(lambda x: self.signup(name, email, password), 2)

    def reset_btn_text_signup(self):
        """
        The reset_btn_text_signup function resets the text of the button to &quot;Proceed&quot; after a user has signed up.


        :param self: Access the attributes and methods of the class in python
        :return: The text of the button
        :doc-author: Trelent
        """

        self.ids['btn'].text = "Proceed"

    async def create_user_account(self, name, email, password):
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
            notify.Notify().notify("Account created successfully")
            self.manager.current = "login"
            self.conn.commit()
            self.reset_btn_text_signup()

            await asynckivy.run_in_thread(lambda: FirebaseManager().add_user(
                name, email, password))
        except sqlite3.IntegrityError:
            self.reset_btn_text_signup()

            notify.Notify().notify("Email already registered", error=True)
