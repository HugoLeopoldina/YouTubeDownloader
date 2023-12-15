import os
os.environ['KIVY_IMAGE'] = 'pil'

from kivy.utils import platform
from kivy.config import Config

import ssl

if platform in ("linux", "win"):
    Config.set('graphics', 'resizable', False)
    Config.set('graphics', 'width', '360')  # Definindo a largura da janela
    Config.set('graphics', 'height', '640') # Definindo a altura da janela
    Config.write()

elif platform == "android":
    from android import mActivity  # type: ignore

    # Eesolvendo a falha na verificação do certificado no android
    ssl._create_default_https_context = lambda: ssl.create_default_context(
        cafile=certifi.where()
    )

import certifi
from kivy.loader import Loader
from kivy.properties import ObjectProperty
from kivymd.tools.hotreload.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from pytube import request

class SM(MDScreenManager):
    def get_classes(self):
        return {screen.__class__.__name__: screen.__class__.__module__ \
            for screen in self.screens}

class MainApp(MDApp):
    AUTORELOADER_PATHS = ["main.py", "mainapp.kv", "data"]
    DEBUG = False if platform != "linux" else True

    current_sm = ObjectProperty(None)
    before_screen = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Youtube Downloader"

        # Intervalo de 2MB
        request.default_range_size = 1048576
        Loader.loading_image = "data/files/loading1.gif"

    def build_app(self, first=False):
        self.set_theme()
        self.sm = SM()

        CLASSES = self.sm.get_classes() 
        KV_FILES = []

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
