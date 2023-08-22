from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from kivymd.uix.anchorlayout import MDAnchorLayout
from kivy.properties import ColorProperty, NumericProperty, StringProperty
# from kivy.clock import Clock
from utils.popup_items import icons
from kivymd.uix.behaviors import CommonElevationBehavior
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.list import ThreeLineAvatarIconListItem, OneLineIconListItem
from kivy.uix.boxlayout import BoxLayout
from models.database import DatabaseManager

from kivymd.uix.bottomsheet import MDCustomBottomSheet
from kivy.factory import Factory
from widgets.popup import Pop


class CircularProgressBar(MDAnchorLayout):
    bar_color_bg = ColorProperty()
    bar_color = ColorProperty()
    set_value = NumericProperty()


class ExpenseList(ThreeLineAvatarIconListItem, MDFloatLayout, CommonElevationBehavior):

    category = StringProperty()
    icon = StringProperty()
    amount = StringProperty()
    date = StringProperty()
    item = StringProperty()
    conn = DatabaseManager().conn
    cursor = conn.cursor()


class Item(OneLineIconListItem):
    pass


class BudgetContent(MDFloatLayout):
    pass


class UpdateBudgetContent(BudgetContent):
    pass
    """
    UpdateBudgetContent is a class that defines the layout for updating the budget in the Money Watch app.

    It inherits from the MDFloatLayout class and provides the necessary widgets and layout for updating the budget.
    """
    pass


Builder.load_file("views/home.kv")


class HomeScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with open('utils/developer_info.txt', 'r') as f:
            self.developer_info = f.read()

        with open('utils/app_info.txt', 'r') as f:
            self.app_info = f.read()

    def info(self):
        """
        The info function displays the app's info in a popup.


        :param self: Access the attributes and methods of the class in python
        :return: The about_pop variable
        :doc-author: Trelent
        """

        items = [
            Item(text=" App", on_press=self.app_popup),
            Item(text="Developer", on_press=self.info_popup),
        ]
        self.about_pop = Pop(title="About...",
                             type="simple",
                             items=items,
                             )
        self.about_pop.open()

    def info_popup(self, _):
        """
        The info_popup function is used to display the information about the developer of this app.
        It displays a popup with his contact details and links to his social media accounts.

        :param self: Access the attributes and methods of the class in python
        :param obj: Pass the object that triggered the callback
        :return: The information about the developer
        :doc-author: Trelent
        """

        self.info_pop = Pop(title="The Developer", text=self.developer_info)
        self.about_pop.dismiss()
        self.info_pop.open()

    def app_popup(self, _):
        """
        The app_popup function displays a popup window with information about the Money Watch app.


        :param self: Access the attributes and methods of the class in python
        :param obj: Pass the object that triggered the callback
        :return: The following:
        :doc-author: Trelent
        """

        self.about_pop.dismiss()

        self.app_pop = Pop(title="Money Watch App", text=self.app_info)
        self.app_pop.open()
