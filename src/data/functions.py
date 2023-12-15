import os
from functools import wraps
from threading import Thread

from kivy.animation import Animation
from kivy.clock import mainthread
from kivy.core.window import Window
from kivy.utils import platform
from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton

from kivy.factory import Factory
from kivymd.uix.snackbar import *
from kivy.metrics import dp

if platform == "android":
    from android import mActivity # type: ignore
    from jnius import autoclass # type: ignore

app = MDApp.get_running_app()
_snackbar = None
_modules = []

import main

def load_kv(module):
    if _modules:
        for m in _modules:
            if module == m:
                return
    _modules.append(module)
    kv = f"{os.path.join(os.path.dirname(os.path.abspath(main.__file__)), *module.split('.'))}.kv"
    MDApp.get_running_app().KV_FILES.append(kv)

def run_in_thread(func):
    # Caso a classe pai de func nâo tenha o atributo wrapper
    # wraps(func) garante que wrapper tenha o mesmo nome
    # e os mesmos atributos da função func da classe 
    @wraps(func)
    def wrapper(*args, **kwargs):
        _func = Thread(target=func, args=args, kwargs=kwargs)
        _func.start()
    return wrapper

def sec_to_time(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%d:%02d:%02d" % (hour, minutes, seconds)

def bytes_to_mb(bytes):
    return float(bytes/1048576)

def get_filesize(stream):
    size = bytes_to_mb(stream.filesize)
    return int("%(size).2f" %({"size":size}))

def animateWidget(widget, args, complete=None):
    anim = Animation(**args)
    if not complete is None:
        anim.bind(on_complete=complete)
    anim.start(widget)

@mainthread
def setWarning(warning, action=["Ok", None]):
    def close(*_):
        _snackbar.dismiss()

    if platform != "android":
        _snackbar = MDSnackbar(
            Factory.MyLabel(
                text="[font=data/files/Mustica]" + warning + "[/font]",
                theme_text_color="Custom",
                text_color="#393231",
            ),
            MDSnackbarActionButton(
                text="[font=data/files/Mustica]" + action[0] + "[/font]",
                theme_text_color="Custom",
                text_color="#8E353C",
                _no_ripple_effect=True,
                on_release=\
                    action[1] if not action[1] is None else close
            ),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            size_hint_x=.9,
            md_bg_color="#E8D8D7",
            duration=2
        )
    else:
        _snackbar = Snackbar(
            text="[font=data/files/Mustica]" + warning + "[/font]",
            snackbar_x="10dp",
            snackbar_y="10dp",
            size_hint_x=(
                Window.width - (dp(10) * 2)
            ) / Window.width,
            buttons=[
                MDFlatButton(
                    text="Close",
                    on_release=close
                ),
                MDFlatButton(
                    text=action[0],
                    md_bg_color=app.theme_cls.primary_color,
                    on_release=\
                        action[1] if not action[1] is None else close
                )
            ]
        )

    _snackbar.open()

def start_service(name):
    context = mActivity.getApplicationContext()
    service_name = str(context.getPackageName()) + ".Service" + name
    service = autoclass(service_name)
    service.start(mActivity, "", "Título teste", "Texto teste", str())
    return service
