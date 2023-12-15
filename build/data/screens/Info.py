from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivymd.uix.screen import MDScreen

from data.functions import load_kv

load_kv(__name__)

class Info(MDScreen):
    instance = ObjectProperty(None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def showDownloadDialog(self):
        if not hasattr(self, "downloadDialog"):
            self.downloadDialog = Factory.DownloadDialog(
                instance=self.instance)
        elif self.downloadDialog.instance != self.instance:
            self.downloadDialog = Factory.DownloadDialog(
                instance=self.instance)
        self.downloadDialog._open()