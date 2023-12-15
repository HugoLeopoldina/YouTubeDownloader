import os
os.environ['KIVY_IMAGE'] = 'pil'

import ssl

import certifi
from kivy.core.window import Window
from kivy.loader import Loader
from kivy.properties import ObjectProperty
from kivy.utils import platform
from kivymd.app import MDApp
from kivymd.icon_definitions import *
from kivymd.uix.button import MDFlatButton
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.scrollview import *
from kivymd.uix.tab import MDTabs
from kivymd.uix.toolbar import MDTopAppBar
from pytube import request

match platform:
    case "linux":
        from kivymd.toast.kivytoast import toast
        Window.size = (360, 640)
        from plyer.platforms.linux import storagepath
    
    case "win":
        from kivymd.toast.kivytoast import toast
        Window.size = (360, 640)
        from plyer.platforms.win import storagepath
    
    case "android":
        # Resolve a falha na verificação do certificado no android
        ssl._create_default_https_context = lambda: ssl.create_default_context(
            cafile=certifi.where()
        )

class SM(MDScreenManager):
    pass

class MainApp(MDApp):
    current_sm = ObjectProperty(None)
    before_screen = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_path = os.path.dirname(__file__)
        self.title = "Youtube Downloader"

        self.main_path = os.path.dirname(__file__)

        # Intervalo de 2MB
        request.default_range_size = 1048576
        Loader.loading_image = \
            os.path.join(self.main_path, "data", "files", "loading1.gif")

    def build(self):
        self.set_theme()
        self.sm = SM()
        return self.sm
    
    def set_theme(self):
        self.theme_cls.material_style = "M3"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Teal"

    def on_pause(self):
        return True

    def bind_key(self, *_):
        return True

if __name__ == "__main__":
    MainApp().run()

