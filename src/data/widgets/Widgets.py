import os, re
from math import trunc
from threading import Thread
from urllib.request import urlopen

from kivy.base import Builder
from kivy.clock import Clock, mainthread
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.properties import (BooleanProperty, DictProperty, ObjectProperty,
                             StringProperty, NumericProperty)
from kivy.uix.behaviors import ButtonBehavior
from kivy.utils import platform
from kivymd.uix.behaviors import (CommonElevationBehavior, MagicBehavior,
                                  RectangularRippleBehavior)
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton, MDIconButton, MDRaisedButton
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.fitimage import FitImage
from kivymd.uix.label import MDLabel
from kivymd.uix.list import OneLineAvatarIconListItem
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.tab import MDTabs
from mutagen.mp4 import MP4
from pytube import YouTube

from data.functions import bytes_to_mb, load_kv, run_in_thread

if platform == "android":
    from android import autoclass  # type: ignore
    from android.permissions import Permission  # type: ignore
    from android.permissions import check_permission  # type: ignore
    from android.permissions import request_permissions  # type: ignore
    from android.storage import app_storage_path  # type: ignore
    from kivymd.toast.androidtoast import toast

else: from kivymd.toast.kivytoast import toast

load_kv(__name__)

class MyLabel(MDLabel):
    pass

class ItemConfirm(OneLineAvatarIconListItem):
    confirm = BooleanProperty(True)
    callback = ObjectProperty()
    divider = None

    def set_bx(self, bx):
        bx.active = True if not bx.active else False
    
    def on_kv_post(self, base_widget):
        if not self.confirm:
            self.ids.bx.group = "1"
        return super().on_kv_post(base_widget)

class CardInfo(
    RectangularRippleBehavior,
    CommonElevationBehavior,
    ButtonBehavior, MDRelativeLayout, MagicBehavior
):
    thumbnail_channel = StringProperty()
    playlist_videos = DictProperty()
    thumbnail_url = StringProperty()
    playlist_cont = StringProperty()
    channel_name = StringProperty()
    description = StringProperty()
    title = StringProperty(" ")
    duration = StringProperty()
    views = StringProperty()
    link = StringProperty()
    type = StringProperty()

    filesize = DictProperty({
        "mp3": 0,
        "mp4": 0
    })

    def __init__(self, **args):
        super(CardInfo, self).__init__(**args)
        
        self.ripple_scale = 0
        self.ripple_duration_in_fast = .2
        
    def on_kv_post(self, base_widget):
        def add(*_):
            if self.type in {"video", "short"}:
                pos = [ self.thumb.x + dp(10),
                self.thumb.y + dp(10) ]
                
                lb = \
f"""
MyLabel:
    size_hint_x: None
    text: str("{self.duration}")
    adaptive_size: True
    pos: {pos}

    canvas.before:
        Color:
            rgba: 0, 0, 0, 1
        RoundedRectangle:
            radius: [dp(5),]
            size: self.size[0] + dp(10), self.size[1] + dp(10)
            pos: self.pos[0] - dp(5), self.pos[1] - dp(5)
"""
                self.add_widget(Builder.load_string(lb))
            
            elif self.type == "playlist":
                pos = [
                    self.thumb.x + (self.thumb.width/2),
                    self.thumb.y
                ]
                size = [
                    self.thumb.width/2,
                    self.thumb.height
                ]

                with self.thumb.canvas.after:
                    Color(0, 0, 0, .7)
                    RoundedRectangle(
                        radius=[0, dp(15), dp(15), 0],
                        size=size,
                        pos=pos
                    )

                center = [
                    self.thumb.center[0] + self.thumb.center[0]/2,
                    self.thumb.center[1]
                ]

                wid = \
f"""
MDBoxLayout:
    pos_hint: {{"center_y":.5}}
    orientation: "vertical"
    adaptive_size: True
    size_hint_x: None
    spacing: dp(10)
    center: {center}
    
    MyLabel:
        size_hint_x: None
        text: str({self.playlist_cont}).replace("video", "")
        font_size: sp(24)

    MDIcon:
        size_hint_x: None
        icon: "playlist-play"
        pos_hint: {{"center_x":.5}}
        font_size: sp(38)
"""
                self.add_widget(Builder.load_string(wid))
            
            elif self.type == "live":
                self.add_widget(FitImage(
                    pos=[self.thumb.pos[0] + dp(10), self.thumb.pos[1]],
                    source="data/files/live.png",
                    size_hint=(None, None)
                ))

        Clock.schedule_once(add)    
        return super().on_kv_post(base_widget)
    
    def update_duration_bg(self, instance, _):
        self._rect.size = instance.width + dp(5), instance.height + dp(5)
        self._rect.pos = [instance.x - dp(2.5), instance.y - dp(2.5)]

class DialogContent(MDBoxLayout):
    download_percenter = StringProperty()
    percenter = ObjectProperty()
    filename = StringProperty()

class MyFloatingButton(MDCard):
    icon = StringProperty()

class MyIconButton(MDIconButton, MagicBehavior):
    def on_release(self):
        self.twist()
        return super().on_release()

class MyMDTabs(MDTabs):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.slipping = None

    def on_touch_move(self, touch):
        if self.collide_point(*touch.pos):
            if touch.dx > 0:
                self.slipping = "right"
            elif touch.dx < 0:
                self.slipping = "left"

            w = self.get_current_tab()

            if self.slipping == "right" and self.current_index == 0:
                if w.to_window(*w.pos)[0] + Window.width > Window.width:
                    return self.on_touch_up(touch)
            
            elif self.slipping == "left" and self.current_index \
                    == len(self.children)-1:
                if w.to_window(*w.pos)[0] < 0:
                    return self.on_touch_up(touch)
    
    def on_carousel_index(self, instance_tabs_carousel, index: int) -> None:
        self.current_index = index
        return super().on_carousel_index(instance_tabs_carousel, index)

class MyCardButton(MDCard):
    primary_text = StringProperty("Primary Text")
    second_text = StringProperty("Second Text")
    icon = StringProperty("git")

class DownloadDialogContent(MDBoxLayout):
    filesize = StringProperty("0")
    progressValue = NumericProperty(0)

class DownloadDialog(MDDialog):
    instance = ObjectProperty()

    def __init__(self, **kwargs):
        self.type = "custom"

        self.buttons = [
            MDFlatButton(
                text="Cancel",
                on_release=self._dismiss
            ),
            MDRaisedButton(
                on_release=self.downloadFile,
                text="Download",
                disabled=True
            )
        ]

        self.chooseFormats = MDDialog(
            title="Choose a format:",
            type="confirmation",
            auto_dismiss=False,
            items=[
                ItemConfirm(
                    confirm=False,
                    text="MP3",
                    callback= lambda chk: \
                        self.changeFormat("mp3", chk)
                ),
                ItemConfirm(
                    confirm=False,
                    text="MP4",
                    callback= lambda chk: \
                        self.changeFormat("mp4", chk)
                )
            ],
            buttons=[
                MDFlatButton(
                    text="Cancel",
                    on_release= lambda *_: \
                        getattr(self, "chooseFormats").dismiss()
                ),
                MDRaisedButton(
                    text="Next",
                    disabled=True,
                    on_release=lambda *_:
                        self._open(format=False)
                )
            ]
        )
        
        self.loadingDialog = MDDialog(
            auto_dismiss=False,
            title="Preparing, please wait",
        ); self.rl = MDRelativeLayout()

        self.rl.add_widget(FitImage(
            source="data/files/loading.png",
            pos_hint={"right":.97, "center_y":.5},
            size_hint=(None, None),
            size=(dp(45), dp(45))
        )); self.loadingDialog.add_widget(self.rl)

        self.content = DownloadDialogContent()
        super(DownloadDialog, self).__init__(**kwargs)
        
        self.playlistVideoStream = list()
        self.videoList = dict()
        self._instance = None
        self.videoCount = 0
    
    def on_kv_post(self, _):
        self.item_list = self.content.item_list
        self.item_list.clear_widgets()

        self.loadingDialog.text = \
            "Getting download stream\n" \
            "Calculating file size"
        
        if self.instance.type == "playlist":
            self.loadingDialog.text = \
                "Getting videos\n" \
                "Getting download stream\n" \
                "Calculating file size"
        
        self.title = f"Download {self.instance.type}"
        self.content_cls = self.content

    def setData(self, check, filesize, videoname):
        self._check = check

        if check.active and not self.videoList.get(str(self.videoCount)):
            self.videoCount += 1
            self.videoList[self.videoCount] = videoname
        elif self.videoList.get(self.videoCount):
            self.videoCount -= 1

        self.buttons[1].disabled = True if not len(self.videoList) > 0 \
            else False
        
        try:
            if self.instance.type != "playlist":
                self.content.filesize = \
                    str(trunc(bytes_to_mb(filesize))) \
                    if check.active else "0"
        except: pass

    def _open(self, format=True):
        if format:
            for i in self.chooseFormats.items:
                if i.ids.bx.active:
                    self.chooseFormats.buttons[1].disabled = True
                    i.ids.bx.active = False
            self.chooseFormats.open()
        else:
            self.chooseFormats.dismiss()
            self.loadingDialog.open()
            Clock.schedule_once(self.getData, 1 if platform == "android" else .4)

    
    def changeFormat(self, format, check):
        self.format = format
        self.chooseFormats.buttons[1].disabled = False \
            if check.active else True
    
    def getData(self, *_):
        if self._instance != self.instance:
            if self.instance.type != "playlist":
                    self.item_list.add_widget(
                        ItemConfirm(
                            text=self.instance.title,
                            callback=lambda *args: self.setData(
                                filesize=self.instance.filesize[self.format],
                                videoname=self.instance.title,
                                check=args[0],
                            )
                        )
                    )
            else:
                for video in self.instance.playlist_videos["videos"]:
                    stream = YouTube(video['link']).streams
                    _data = self.getStreamFileSize(self.format, stream)

                    data = {"title":video["title"], "stream":_data[1], "filesize":_data[0]}
                    self.playlistVideoStream.append(data)

                    def make_callback(data):
                        def wrapper(*args):
                            self.setData(args[0], data["filesize"], data["title"])
                        return wrapper

                    self.setData(0, data["filesize"], data["title"])
                    self.item_list.add_widget(
                        ItemConfirm(
                            text=video["title"],
                            callback=make_callback(data)
                            )
                    )
            self._instance = self.instance

        if self.instance.type in {"video", "short"}:
            if self.instance.filesize[self.format] == 0:
                self.yt_instance = YouTube(
                    on_progress_callback=self.on_progress_callback,
                    on_complete_callback=self.on_complete_callback,
                    url=self.instance.link,
                )

                stream = self.yt_instance.streams
                s = self.getStreamFileSize(self.format, stream)

                self.instance.filesize[self.format] = s[0]
                self.stream = s[1]

                self.update()
            else: self.update()
        
        elif self.instance.type == "playlist":
            self.update()
    
    def getStreamFileSize(self, format, stream):
        # while True:
            # try:
        if format == "mp3":
            _stream = stream.get_audio_only()
            return [_stream.filesize, _stream]
        elif format == "mp4":
            _stream = stream.get_highest_resolution()
            return [_stream.filesize, _stream]
            # except: pass

    @mainthread
    def update(self, *_):
        self.loadingDialog.dismiss()
        if hasattr(self, "_check"):
            self.setData(self._check, 0, str())
        self.open()
    
    @mainthread
    def _dismiss(self, *_):
        if (hasattr(self, "_check")
            and self._check.active):
            self.buttons[1].disabled = True
            self.content.filesize = "0"
            self._check.active = False
            self.videoList.clear()
            self.videoCount = 0
        self.dismiss()
    
    @mainthread
    def downloadFile(self, *_):
        self.content.progress.start()
        
        @run_in_thread
        def _run(*_):
            self.filename = f"{self.instance.title}.{self.format}"
            self.filename = re.sub(r'[\\/*?:"<>|]', '_', self.filename)
            
            if platform == "android":
                def _run(*_):
                    def _download(*_):
                        self.out_file = self.stream.download(
                            output_path=app_storage_path()
                        )
                    Thread(target=_download).start() 
                _run()
                
                # permissions = [
                #     Permission.WRITE_EXTERNAL_STORAGE,
                #     Permission.READ_EXTERNAL_STORAGE
                # ]

                # self.checkPermissions(
                #     false_call=self._dismiss,
                #     permissions=permissions,
                #     true_call=_run
                # )
            
            else:
                from plyer import storagepath
                self.out_file = \
                self.stream.download(
                    filename=self.filename,
                    output_path=os.path.join(storagepath.get_downloads_dir(), "YTDL")
                )
        _run()
    
    @staticmethod
    @mainthread
    def checkPermissions(
        permissions:list=[],
        true_call:object=None,
        false_call:object=None
    ):
        @mainthread
        def _check(*_):
            if not all(map(lambda perm: \
                check_permission(perm), permissions)):
                false_call()
            else: true_call()
        
        if not all(map(lambda perm: \
            check_permission(perm), permissions)):
            request_permissions(permissions, _check)
        else: true_call()

    @mainthread
    def on_progress_callback(self, stream, _, bytes_remaining):
        self.content.progressValue = \
            int(100 - float((bytes_remaining*100)/
                stream.filesize))
        
    @mainthread
    def on_complete_callback(self, *_):
        if self.content.progress.value != 100:
            self.content.progress.value = 100
        
        def _extra(*_):
            """
            tags = ["\xa9nam", "\xa9ART", "\xa9wrt", "\xa9alb",
                "\xa9gen", "gnre", "trkn", "disk",
                "\xa9day", "cpil", "pgap", "pcst", "tmpo",
                "\xa9too", "----", "covr", "\xa9lyr"]
            """

            thumb_data = urlopen(self.yt_instance.thumbnail_url).read()
            metadata = MP4(self.out_file)

            try: metadata.add_tags()
            except: pass

            metadata["\xa9ART"] = self.yt_instance.author
            metadata["covr"] = [thumb_data]
            metadata.save()

            if self.format == "mp3":
                base, _ = os.path.splitext(self.out_file)
                new_file = base + ".mp3"
                os.rename(self.out_file, new_file)

            if platform == "android":
                from androidstorage4kivy import SharedStorage  # type: ignore
                Environment = autoclass("android.os.Environment")
                Shared = SharedStorage()

                Shared.copy_to_shared(
                    collection=Environment.DIRECTORY_DOWNLOADS,
                    private_file=new_file if self.format == \
                        "mp3" else self.out_file
                )

                os.remove(new_file if self.format == "mp3" else self.out_file)
            
            @mainthread
            def complete(*_):
                self.content.progressValue = 0
                self.content.progress.stop()
                if platform != "android": toast("Download concluído!")
                else: toast("Download concluído!", False, 80, 200, 0)

            Clock.schedule_once(complete)
        Clock.schedule_once(_extra)
        return