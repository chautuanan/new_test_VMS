import cv2
import kivy
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.anchorlayout import AnchorLayout
from queue import Queue
from threading import Thread
import numpy as np
from kivy.graphics.texture import Texture

kivy.require('2.1.0')  # Đảm bảo phiên bản Kivy phù hợp


def stream_camera(camera_url, camera_name, frame_queue):
    cap = cv2.VideoCapture(camera_url)
    if not cap.isOpened():
        print(f"Không thể mở camera {camera_name}")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print(f"Lỗi khi đọc từ {camera_name}")
            break

        frame_resized = cv2.resize(frame, (640, 480))
        frame_flipped = cv2.flip(frame_resized, 0)  # 0 là lật dọc
        frame_rgb = cv2.cvtColor(frame_flipped, cv2.COLOR_BGR2RGB)
        frame_queue.put(frame_rgb)

    cap.release()


class WelcomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = GridLayout(cols=1, spacing=0, padding=0)
        welcome_label = Label(text="Chào mừng đến với VMS của An", font_size=24)
        view_button = Button(text="Xem Camera", size_hint=(1, 0.2))
        view_button.bind(on_press=self.go_to_camera_screen)
        layout.add_widget(welcome_label)
        layout.add_widget(view_button)
        self.add_widget(layout)

    def go_to_camera_screen(self, instance):
        self.manager.current = 'camera_screen'


class CameraScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Tạo GridLayout để chứa các luồng camera
        self.grid = GridLayout(cols=4, padding=0, spacing=0)
        self.labels = []
        self.frame_queues = []
        for i in range(len(camera_urls)):
            frame_queue = Queue(maxsize=0)
            self.frame_queues.append(frame_queue)

            img = Image()
            self.grid.add_widget(img)
            self.labels.append(img)

            camera_name = f"Camera {i + 1}"
            Thread(target=stream_camera, args=(camera_urls[i], camera_name, frame_queue), daemon=True).start()
            self.update_label(img, frame_queue)

        # Tạo AnchorLayout để đặt nút "Back" ở góc trên trái
        anchor_layout = AnchorLayout(anchor_x='left', anchor_y='top')
        back_button = Button(text="Back", size_hint=(0.05, 0.05))
        back_button.bind(on_press=self.go_back_to_welcome)
        anchor_layout.add_widget(back_button)

        # Thêm GridLayout và AnchorLayout vào màn hình
        self.add_widget(self.grid)
        self.add_widget(anchor_layout)

    def update_label(self, img, frame_queue):
        if not frame_queue.empty():
            frame_rgb = frame_queue.get()
            texture = Texture.create(size=(frame_rgb.shape[1], frame_rgb.shape[0]), colorfmt='rgb')
            texture.blit_buffer(frame_rgb.tobytes(), colorfmt='rgb', bufferfmt='ubyte')
            img.texture = texture

        Clock.schedule_once(lambda dt: self.update_label(img, frame_queue), 0.01)

    def go_back_to_welcome(self, instance):
        self.manager.current = 'welcome_screen'


class CameraApp(App):
    title = "VMS của An"
    def build(self):
        sm = ScreenManager()
        sm.add_widget(WelcomeScreen(name='welcome_screen'))
        sm.add_widget(CameraScreen(name='camera_screen'))
        return sm


if __name__ == "__main__":
    camera_urls = [
        "rtsp://rtsp:rtsp1234@tinhocngoisao.ruijieddns.com:9190/rtsp/streaming?channel=01&subtype=0",
        "rtsp://rtsp:rtsp1234@tinhocngoisao.ruijieddns.com:9190/rtsp/streaming?channel=02&subtype=0",
        "rtsp://rtsp:rtsp1234@tinhocngoisao.ruijieddns.com:9190/rtsp/streaming?channel=03&subtype=0",
        "rtsp://rtsp:rtsp1234@tinhocngoisao.ruijieddns.com:9190/rtsp/streaming?channel=04&subtype=0",
        "rtsp://rtsp:rtsp1234@tinhocngoisao.ruijieddns.com:9190/rtsp/streaming?channel=05&subtype=0",
        "rtsp://rtsp:rtsp1234@tinhocngoisao.ruijieddns.com:9190/rtsp/streaming?channel=06&subtype=0",
        "rtsp://rtsp:rtsp1234@tinhocngoisao.ruijieddns.com:9190/rtsp/streaming?channel=07&subtype=0",
        "rtsp://rtsp:rtsp1234@tinhocngoisao.ruijieddns.com:9190/rtsp/streaming?channel=08&subtype=0",
        "rtsp://rtsp:rtsp1234@tinhocngoisao.ruijieddns.com:9190/rtsp/streaming?channel=09&subtype=0",
        "rtsp://rtsp:rtsp1234@tinhocngoisao.ruijieddns.com:9190/rtsp/streaming?channel=10&subtype=0",
        "rtsp://rtsp:rtsp1234@tinhocngoisao.ruijieddns.com:9190/rtsp/streaming?channel=11&subtype=0",
        "rtsp://rtsp:rtsp1234@tinhocngoisao.ruijieddns.com:9190/rtsp/streaming?channel=12&subtype=0"
    ]

    CameraApp().run()
