from kivy.app import App

from kivy.uix.button import Button
from kivy.uix.video import Video
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.image import Image

from kivy.lang import Builder

from kivy.clock import Clock

from kivy.core.window import Window

from kivy.graphics.texture import Texture

from ultralytics import YOLO
import cv2


import time

import uart_com 

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.layout = FloatLayout()
        
        self.video = Video(source='asset/output_video-vmake.mp4', state='play', options={'eos': 'loop'})
        self.video.size_hint = (1, 1)
        self.video.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        self.layout.add_widget(self.video)
        
        masukkan_button = Button(text='Masukkan Botol', font_size=18, size_hint=(None, None), size=(250, 150), pos_hint={'center_x': 0.75, 'center_y': 0.5})
        masukkan_button.bind(on_press=self.open_second_Window)
        self.layout.add_widget(masukkan_button)
        
        self.add_widget(self.layout)
    
    def open_second_Window(self, instance):
        self.manager.current = 'second_Window'

class SecondWindow(Screen):
    def __init__(self, uart_instance,**kwargs):
        super().__init__(**kwargs)
        self.clock_event = None 
        self.capture = None
        self.model = None
        self.start_time = None
        self.uart = uart_instance

        layout = FloatLayout()
        self.image = Image(size_hint=(1,1), pos_hint ={'center_x':0.5, 'center_y':0.5})
        layout.add_widget(self.image)

        self.result_label = Button(text="Detecting...", font_size=18, size_hint=(None, None), size=(250, 50), pos_hint={'center_x': 0.5, 'center_y': 0.1})
        layout.add_widget(self.result_label)

        back_button = Button(text='Kembali', font_size=18, size_hint=(None, None), size=(250, 150), pos_hint={'center_x': 0.75, 'center_y': 0.5})
        back_button.bind(on_press=self.go_back)
        layout.add_widget(back_button)

        self.add_widget(layout)
    
    def on_enter(self):
        self.start_time = time.time()

        self.all_detections = []

        self.model = YOLO("yolo11m.pt")
        self.capture = cv2.VideoCapture(0)
        
        if not self.capture.isOpened():
            print("Error: Could not open webcam.")
            return
        self.clock_event = Clock.schedule_interval(self.load_video, 1.0/30.0)

    def load_video(self, *args):
        
        ret, frame = self.capture.read()
        if not ret:
            print("Failed to capture frame")
            return

        result = self.model(frame)

        detections = [self.model.names[int(i)] for i in result[0].boxes.cls] if result[0].boxes else [] 
        self.all_detections.extend(detections)

        unique_detections = list(set(self.all_detections))
        detected_objects = ", ".join(set(unique_detections)) if unique_detections else "No objects detected"
        if "bottle" in unique_detections:
            self.uart.send("1")
        elif "can" in unique_detections:
            self.uart.send("2")
        else:
            self.uart.send("0")
        # annotated_frame = cv2.flip(annotated_frame, 0)
        # buf = annotated_frame.tobytes()
        # texture = Texture.create(size=(annotated_frame.shape[1], annotated_frame.shape[0]), colorfmt='bgr')
        # texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        # self.image.texture = texture

        if time.time() - self.start_time >= 0.5:
            self.result_label.text = f"Hasil Deteksi:\n{detected_objects}"
            self.stop_camera()

    def stop_camera(self):
        if self.capture:
            self.capture.release()
        if self.clock_event:
            self.clock_event.cancel()
        self.clock_event=None
        self.capture = None

    def go_back(self, instance):
        self.stop_camera()
        self.manager.current = 'main'

class FullscreenApp(App):
    def build(self):
        Window.fullscreen = 'auto'  # Make the window fullscreen
        Window.bind(on_key_down=self.on_key_down)
        
        self.uart = uart_com.Uart(port="/dev/serial/by-id/usb-1a86_USB_Serial-if00-port0",
                                  baudrate=115200,
                                  timeout=1)

        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(SecondWindow(uart_instance=self.uart,name='second_Window'))
        
        return sm
    
    def on_key_down(self, instance, key, *args):
        if key == 27:  # 27 is the keycode for Esc
            self.uart.close()
            App.get_running_app().stop()

if __name__ == "__main__":
    FullscreenApp().run()
