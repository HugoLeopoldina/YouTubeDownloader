from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import ObjectProperty
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.tab import MDTabsBase

from data.functions import load_kv

load_kv(__name__)

class MyTab(MDFloatLayout, MDTabsBase):
    pass

class Main(MDScreen):
    instance = ObjectProperty(None)

    def __init__(self, *args, **kwargs):
        super(Main, self).__init__(*args, **kwargs)
        Window.bind(on_keyboard=self.back_click)

        self.before_time = Clock.get_time()
    
    def back_click(self, _, key, *args):
        if key == 27:
            if (hasattr(self.ids.info, "downloadDialog") and
                self.ids.info.downloadDialog._is_open):
                self.ids.info.downloadDialog.dismiss()
                return True
            
            if (Clock.get_time() - self.before_time) > 1:
                self.before_time = Clock.get_time()
                try:
                    if self.sm.current == "info":
                        self.sm.info.play.opacity = 0
                        if len(self.sm.current_heroes) == 0:
                            self.sm.current_heroes = ["video_thumb", "channel_thumb"]
                        self.sm.transition.direction = "right"
                        self.sm.current = "search"
                        
                    elif self.sm.current == "tools":
                        self.sm.transition.direction = "down"
                        self.sm.current = "info"
                except: self.sm.current_heroes = []
        return True

    def on_kv_post(self, base_widget):
        # self.sm.current = "info"
        return super().on_kv_post(base_widget)