from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from widgets.notify import Notify
from widgets.popup import Pop
from widgets.button import FlatButton

Builder.load_file("views/otp.kv")


class OtpScreen(MDScreen):
    notify = Notify()

    ERROR = "error"
    CORRECT = "correct"

    ['null', 'text', 'number', 'url', 'mail', 'datetime', 'tel', 'address']

    def validate_otp(self, otp):
        if not isinstance(otp, str) or not otp.isnumeric():
            self.notify.notify("Invalid OTP", error=True)
            return "error"
        otps = self.get_otp_lbl_id().text

        if otp != otps:
            self.notify.notify("OTP is not correct", error=True)
            return self.ERROR
        else:
            return self.CORRECT

    def get_otp_lbl_id(self):
        """
        The get_otp_lbl_id function returns the otp_lbl id from the .kv file.
            This is used to set the text of this label in other functions.

        :param self: Represent the instance of the class
        :return: The id of the label
        :doc-author: Trelent
        """

        otp = self.ids['otp_lbl']
        return otp
