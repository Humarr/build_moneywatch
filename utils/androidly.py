
import os

from kivy.utils import platform
# from kivymd.toast import toast
# import androidstorage4kivy
# from widgets import notify
# import Notify
# import firebase
# from plyer import storagepath
# storage_desktop = storagepath.get_home_dir()
# storage_android = storagepath.get_external_storage_dir()


class Storage:
    """checks permissions for android"""
    # def __init__(self):
    #     """checks permissions for android
    #     """

    def storage(self):
        """
        The storage function returns the path to the user's storage directory.
        This is where we will save our data files.

        :param self: Access variables that belongs to the class
        :return: The path to the storage folder
        :doc-author: Trelent
        """

        if platform == "linux" or platform == "win" or platform == "macosx":
            from plyer import storagepath
            storage_desktop = storagepath.get_home_dir()
            return storage_desktop
            # return storage_android

        if platform == "android":
            # try:
            from plyer import storagepath
            from kivy.core.window import Window
            Window.softinput_mode = "below_target"

            # from pythonforandroid.recipes.android.src.android.permissions import Permission, request_permissions, check_permission, PERMISSION_DENIED, PERMISSION_GRANTED
            from android.permissions import Permission, request_permissions, check_permission, PERMISSION_DENIED, PERMISSION_GRANTED
            # from android import api_version, mActivity
            # from jnius import autoclass, cast
            # ok = check_permission
            # import pythonforandroid.recipes.android.src.android.permissions

            if PERMISSION_DENIED:
                # if not check_permission(Permission.READ_EXTERNAL_STORAGE) or not check_permission(Permission.WRITE_EXTERNAL_STORAGE):
                request_permissions(
                    [Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
                # , Permission.WRITE_CONTACTS, Permission.READ_CONTACTS])
            # elif PERMISSION_GRANTED:

                # PythonActivity = autoclass('org.kivy.android.PythonActivity')
                # Environment = autoclass('android.os.Environment')
                # context = cast('android.content.Context',
                #                PythonActivity.mActivity)
                # global storage_android
                # storage_android = context.getExternalFilesDir(
                #     '.Money Watcher').getAbsolutePath()

                path = storagepath.get_downloads_dir() # get the downloads directory path
                storage_android = os.mkdir(f"{path}/.moneywatch") # make a hidden folder where we can store our databases and other important files

                """Returns the android storage  path"""

                # print(f"ANDROID:: {storage_android}")
            return storage_android

            # from kvdroid.tools.path import sdcard

            # app = ".money_watcher"

            # self.read = Permission.READ_EXTERNAL_STORAGE
            # self.write = Permission.WRITE_EXTERNAL_STORAGE
            # if PERMISSION_DENIED:
            #     request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
            #     print(app)

            # if PERMISSION_GRANTED:
            #     storage_android = f"{sdcard()}/{app}"
            #     print(storage_android)
            #     print(f"ANDROID:: {storage_android}")
            # print(f"ANDROID:: {storage_android}")
            # return storage_android

            # return storage_android
            # sdcard()
            # return external_storage
        elif platform == "ios":
            from widgets import notify
            notify.Notify().notify("Not supported on IOS at the moment.\You can try it on your mac")

# print(Storage().storage())


class Emailer:
    # TODO: enable sending of emails  in subsequent releases
    # def email_send(self, recipient, subject, body):

    def email_send(self, recipient, subject, body):
        """
        The email_send function sends an email to the specified recipient with the specified subject and body.


        :param self: Access the class attributes and methods
        :param recipient: Specify the recipient of the email
        :param subject: Set the subject of the email
        :param body: Send the message body
        :return: None
        :doc-author: Trelent
        """

        try:
            if platform == "android":
                from kvdroid.tools.email import send_email
                send_email(self, recipient, subject, body)
                print("email")
            else:
                from plyer import email
                email.send(recipient=recipient, subject=subject, text=body)
        except Exception as e:
            print(f"Email Exception:: {e}")
            from widgets import notify
            notify.Notify().notify("Network error", error=True)

    # from kvdroid.tools.email import send_email
    # from os import getenv
    # from os.path import join
    # send_email(
    #     recipient=["test@gmail.com"],
    #     subject="Hello there",
    #     body="This is kvdroid",
    #     file_path=join(getenv("PYTHONHOME"), "test.txt")
    # )


class Sms:
    if platform == "android":
        def get_sms(self):
            from kvdroid.tools.sms import get_all_sms
            # from kivy.storage.jsonstore import JsonStore
            # sms_store = JsonStore(f"{Storage().storage()}/sms.json")
            # from pythonforandroid.recipes.android.src.android.permissions import Permission, request_permissions, PERMISSION_DENIED, PERMISSION_GRANTED  # NOQA
            # # remember to add READ_SMS to your buildozer `android.permissions`
            # if PERMISSION_DENIED:
            #     request_permissions([Permission.READ_SMS, Permission.SEND_SMS])
            # if PERMISSION_GRANTED:
            # returns a tuple of message count and messages
            # print(get_all_sms())
            sms = get_all_sms()
            # print(f"Messages:: {sms}")
            with open(f"{Storage().storage()}/sms.txt", "a") as sms_store:

                sms_store.write(sms)
    else:
        def send_sms(self, recepient, message):
            """
            The send_sms function sends a text message to the specified recepient.
            It takes two arguments: 
                - recepient (str) : The phone number of the recipient in E.164 format, i.e., '+12223334444'
                - message (str) : The content of the text message

            :param self: Access the attributes and methods of the class in python
            :param recepient: Specify the number to which the message is to be sent
            :param message: Store the message that is to be sent
            :return: The message that was sent to the recepient
            :doc-author: Trelent
            """

            from plyer import sms
            sms.send(recepient, message)


class Notification:
    # TODO: enable notifications in subsequent releases
    # if platform == "android":
    # pass
    def notification(self, title, text, icon_path, color_icon=None):
        """
        The notification function is used to send a notification to the user.
        It takes in 4 parameters: title, text, icon_path and color_icon.
        The title parameter is the name of the app that will be displayed on top of 
        the notification bar. The text parameter displays a message for the user when 
        the notification pops up. The icon_path parameter specifies where your image file is located on your computer and color_icon specifies what colour you want your app icon to be.

        :param self: Access variables that belongs to the class
        :param title: Set the title of the notification
        :param text: Display the message
        :param icon_path: Specify the path of the icon that is to be displayed on the notification
        :param color_icon: Change the color of the icon
        :return: None
        :doc-author: Trelent
        """

        try:
            if platform == "android":
                from kvdroid.jclass.android.graphics import Color
                from kvdroid.tools.notification import create_notification
                from kvdroid.tools import get_resource

                create_notification(
                    small_icon=get_resource(
                        "drawable").ico_nocenstore,  # app icon
                    channel_id="1", title=f'{title}',
                    text=f"{text}",
                    ids=1, channel_name=f"ch1",
                    large_icon=f"{icon_path}",
                    expandable=True,
                    # 0x00 0xC8 0x53 is same as 00C853
                    small_icon_color=Color().rgb(f"{color_icon}"),
                    # big_picture="assets/image.png"
                )

            else:
                from plyer import notification
                notification.notify(title=title, message=text,
                                    app_name="", app_icon=icon_path)

        except Exception as e:
            print(f"Exception for Notification:: {e}")
            from plyer import notification
            notification.notify(title=title, message=text,
                                app_name="", app_icon=icon_path)


class Contact:

    # TODO: enable reading and writing to contacts in subsequent releases
    def get_contact(self):
        if platform == "android":
            print("contacts")
            from pythonforandroid.recipes.android.src.android.permissions import Permission, request_permissions, PERMISSION_DENIED, PERMISSION_GRANTED  # NOQA
            # remember to add READ_CONTACT to your buildozer `android.permissions`
            if PERMISSION_DENIED:
                request_permissions(
                    [Permission.READ_CONTACTS, Permission.WRITE_CONTACTS])
                from kvdroid.tools.contact import get_contact_details
                # gets a dictionary of all contact both contact name and phone mumbers
                phone_book = get_contact_details("phone_book")
                # gets a list of all contact names
                names = get_contact_details("names")
                # gets a list of all contact phone numbers
                mobile_no = get_contact_details("mobile_no")
