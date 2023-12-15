import re
from functools import partial

import httpx._exceptions
from kivy.clock import Clock, mainthread
from kivy.factory import Factory
from kivy.metrics import sp
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from youtubesearchpython import Playlist, Search, Video

from data.functions import (animateWidget, load_kv, run_in_thread, sec_to_time,
                            setWarning)
from data.widgets.Widgets import CardInfo, MyIconButton

load_kv(__name__)

class SearchVideos(MDScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.loading = Factory.MyModalView()
        self.before_time = Clock.get_time()
        self.app = MDApp.get_running_app()
        self.search_controll = str()
        self.query_controll = False
        self.click_controll = True
        self.progress_value = 1
        self.video_url = False
        self.videolen = -1

        self.playlist_pattern = \
            (r"^(?:https?:\/\/)?(?:www\.)?youtube\."
            "com\/(?:playlist\?|watch\?."
            "*list=)([a-zA-Z0-9_-]+)")

        self.video_pattern = \
            (r'(https?://)?(www\.)?'
            '(youtube|youtu|youtube-nocookie)\.(com|be)/'
            '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')

        self.plus_button = MyIconButton(
            text_color=self.app.theme_cls.primary_color,
            on_release=lambda *_: self.moreQuery(),
            theme_text_color="Custom",
            pos_hint={"center_x":.5},
            _no_ripple_effect=True,
            icon_size=sp(36),
            icon="plus"
        )

    @run_in_thread
    def getResult(self, query):
        if query in {str(), self.search_controll}:
            return
        
        self.setLoadingScreen()
        match = partial(re.match, string=query)

        try:
            if match(pattern=self.playlist_pattern):
                try: 
                    self.videos = Playlist.getVideos(query)
                    self.results = Playlist.getInfo(query)
                    self.query_controll = True
                    self.results["type"] = "playlist"

                except KeyError:
                    setWarning(
                        warning="Playlist privada",
                        action=["Autenticar", None]
                    ); return
                
                except:
                    setWarning(
                        warning="Link inválido"
                    ); return
                
                finally:
                    self.loading._progress.value = 100
                    self.progress_value = 1

            elif match(pattern=self.video_pattern):
                try:
                    self.results = Video.getInfo(query)
                    self.query_controll = True
                    self.results["type"] = "video"
                    self.video_url = True

                except ValueError:
                    try:
                        video_id = query.split("/")[-1].split("?")[0]
                        query = f"https://www.youtube.com/watch?v={video_id}"
                        self.results = Video.getInfo(query)
                        self.query_controll = True
                        self.results["type"] = "short"

                    except IndexError:
                        setWarning(
                            warning="Link inválido",
                        ); return
                self.video_url = True
                    
            else:
                self.query = Search(query, limit=8)
                self.results = self.query.result().get("result")

                if len(self.results) == 0:
                    self.query = Search(query.replace("/", ""), limit=9)
                    self.results = self.query.result().get("result")
                    
                    # Canal?
                    if len(self.results) == 0:
                        self.loading._progress.value = 100
                        self.loading.dismiss()
                        return
                    
                self.query_controll = True
                self.search_controll = query

            self.updateUi()

        except httpx.ConnectError:
            self.loading._progress.value = 100
            setWarning(warning="Sem conexão")
    
    @mainthread
    def setLoadingScreen(self):
        self.loading.open()
        Clock.schedule_interval(self._setLoadingValue, .05)
    
    def _setLoadingValue(self, *_):
        if self.loading._progress.value < 100:
            if self.loading._progress.value >= 50 and not self.query_controll:
                self.progress_value = 0
            self.loading._progress.value += self.progress_value
        else:
            self.loading.dismiss()
            self.progress_value = 1
            Clock.schedule_once(
                lambda *_: setattr(
                    self.loading._progress,
                    "value", 0
                ), .2
            )
            return False

    @mainthread
    def updateUi(self, clear:bool=True):
        if len(self.results) == 0:
            setWarning(warning="Sem resultados")
            self.loading._progress.value = 100

        self.progress_value = 10

        if clear: self.videolist.clear_widgets()
        else: self.videolist.remove_widget(self.plus_button)

        checkinstance = partial(isinstance, self.results)

        if checkinstance(list):
            for index, video in enumerate(self.results):
                self.videolen += 1
                self.addVideo(**video)

            try:
                self.scroll.scroll_to(
                    self.videolist.children[self.videolen])
            except IndexError:
                try:
                    self.scroll.scroll_to(
                        self.videolist.children[-1])
                except: pass
                
            self.videolen = 0
            self.videolist.add_widget(self.plus_button)
            
        elif checkinstance(dict):
            self.addVideo(**self.results)
        
        if self.scroll.disabled:
            self.scroll.disabled = False
    
    def addVideo(self, **kwargs):
        if kwargs.get("type") == "channel":
            return
        
        elif kwargs.get("type") == "playlist":
            kwargs["viewCount"] = {"short":kwargs["viewCount"] if \
                kwargs.get("viewCount") else " "}
            kwargs["duration"] = "0:0"

            
            if kwargs.get("thumbnails") is None:
                video = Playlist.getVideos(kwargs["link"]).get("videos")[0]
                kwargs["thumbnails"] = \
                    [{"url":video["thumbnails"][1]["url"]}]
            
            # if int(len(self.videos["videos"])) < int(kwargs["videoCount"]):
            #     count = int(kwargs["videoCount"]) - int(len(self.videos["videos"]))
            #     setWarning(warning=f"{count} vídeos indisponíveis estão ocultos")
        
        else:
            kwargs["videoCount"] = str()
            self.videos = dict()

            if self.video_url:
                self.video_url =False
                kwargs["thumbnails"] = \
                    [kwargs["thumbnails"][1]]

            if (kwargs.get("isLiveNow") and kwargs["isLiveNow"]) or \
                kwargs["duration"] is None:
                kwargs["duration"] = ""
                kwargs["type"] = "live"
                kwargs["viewCount"]["short"] = " "

            if isinstance(kwargs["duration"], dict):
                kwargs["duration"] = \
                    str(sec_to_time(
                        int(kwargs["duration"]["secondsText"]))
                    )
            
            if not kwargs["viewCount"].get("short"):
                kwargs["viewCount"]["short"] = kwargs["viewCount"]["text"]
                kwargs["viewCount"].pop("text")
            
            if kwargs["viewCount"]["short"] is None:
                kwargs["viewCount"]["short"] = ""

        if not kwargs["channel"].get("thumbnails"):
            kwargs.get("channel")["thumbnails"] = \
                [{"url":"data/files/pre.png"}]
        
        self.videolist.add_widget(
            CardInfo(
                thumbnail_channel=kwargs["channel"]["thumbnails"][0]["url"],
                thumbnail_url=kwargs["thumbnails"][0]["url"],
                channel_name=kwargs["channel"]["name"],
                playlist_cont=kwargs["videoCount"],
                views=kwargs["viewCount"]["short"],
                on_release=self.runInfoScreen,
                duration= kwargs["duration"],
                playlist_videos=self.videos,
                title=kwargs["title"],
                link=kwargs ["link"],
                type=kwargs["type"],
            )
        )
    
    def runInfoScreen(self, instance):
        if self.click_controll:
            infoscreen = self.parent.info
            self.instance = infoscreen.instance = instance
            instance.opacity = 0
            objs = instance.ids

            self.temp_video_thumb.opacity = 1
            self.temp_channel_thumb.opacity = 1

            infoscreen.to_title.text = instance.title
            infoscreen.to_duration.text = instance.duration
            infoscreen.to_channel_name.text = instance.channel_name
            infoscreen.to_views.text = instance.views
            infoscreen.to_type.text = \
                "Type: [color=#FFFFFF]" + instance.type + "[/color]"

            self.from_video_thumb.size = objs.thumb.size
            self.from_video_thumb.pos = objs.thumb.to_window(*objs.thumb.pos)
            self.temp_video_thumb.source = objs.thumb.source

            self.from_channel_thumb.size = objs.channel.size
            self.from_channel_thumb.pos = objs.channel.to_window(*objs.channel.pos)
            self.temp_channel_thumb.source = objs.channel.source

            infoscreen.videos_count.text = instance.playlist_cont

            self.parent.current_heroes = ["video_thumb", "channel_thumb"]
            self.parent.transition.direction = "left"
            self.parent.current = "info"
            self.click_controll = False
    
    @run_in_thread
    def moreQuery(self):
        self.setLoadingScreen()
        self.query.next(); self.query.limit = 10
        self.results = self.query.result().get("result")
        self.updateUi(clear=False)
    
    def hide_temp(self, *_):
        self.instance.opacity = 1

        animateWidget(
            widget=self.temp_video_thumb,
            args={"opacity":0, "duration":.15}
        )

        animateWidget(
            widget=self.temp_channel_thumb,
            args={"opacity":0, "duration":.15},
            complete=lambda *_: setattr(self, "click_controll", True)
        )
