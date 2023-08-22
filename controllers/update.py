from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
import re

from models.database import DatabaseManager
from models.firebase_db import FirebaseManager
from widgets.notify import Notify

from kivy.clock import Clock, mainthread
import asynckivy

Builder.load_file("views/update.kv")


class UpdateScreen(MDScreen):
    conn = DatabaseManager().conn
    cursor = conn.cursor()

    def validate_password(self, password):
        reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$"

        # compiling regex
        pat = re.compile(reg)

        # searching regex
        valid = re.search(pat, password)

        if valid:
            self.ids['new_password'].error = False
            return True
        else:
            self.ids['new_password'].error = True
            return False

    def compare_passwords(self, new_password, confirm_password):
        if new_password != confirm_password:
            self.ids['confirm_password'].error = True
            # print("match not")
            self.ids['confirm_password'].helper_text = "Passwords do not match"
            return False
        else:
            self.ids['confirm_password'].error = False
            # print("matches")
            return True

    async def update_password(self, new_password, confirm_password):
        if self.validate_password(new_password) and self.compare_passwords(new_password, confirm_password):
            # print("yoyo")
            try:
                email = self.manager.get_screen("forgot").ids['email'].text
            except Exception:
                Notify().notify("Unable to get email", error=True)
            sql = "UPDATE user_info SET password = ? WHERE email=?"
            self.cursor.execute(sql, (new_password, email))
            self.conn.commit()
            Notify().notify("Password Updated successfully")
            self.manager.current = "login"
            await asynckivy.run_in_thread(lambda:  FirebaseManager().update_password(email, new_password))
        else:
            Notify().notify("Check your passwords and try again", error=True)
