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
import time

from ultralytics import YOLO
import cv2
# import numpy as np
import math
import cvzone
from sort import *

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
    def __init__(self, **kw):
        super().__init__(**kw)

        self.clock_event = None
        self.capture = None
        self.model = None
        
        layout =FloatLayout()
        self.image = Image(size_hint = (1,1), pos_hint = {'center_x':0.5, 'center_y':0.5})
        layout.add_widget(self.image)

        self.result_label = Button(text="Detecting...", font_size=18, size_hint=(None, None), size=(250, 50), pos_hint={'center_x': 0.5, 'center_y': 0.1})
        layout.add_widget(self.result_label)

        back_button = Button(text="Kembali", font_size=18,size_hint=(None, None),size=(250,250),pos_hint={'center_x': 0.75,'center_y':0.5})
        back_button.bind(on_press=self.go_back)
        layout.add_widget(back_button)
        
        self.add_widget(layout)

class SecondWindow(Screen):

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.clock_event = None 
        self.capture = None
        self.model = None
        self.start_time = None
        # self.uart = uart_instance

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

        self.model = YOLO('asset/best.pt')
        self.capture = cv2.VideoCapture(0)

        self.width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.line = [self.width - (self.width // 4), 0, self.width - (self.width // 4), self.height]
        self.counterin = []

        self.trackers = Sort(max_age=20,min_hits=3)
        if not self.capture.isOpened():
            print("Error: Could not open webcam.")
            return
        self.clock_event = Clock.schedule_interval(self.load_video, 1.0/30.0)

    def load_video(self, *args):
        ret, frame = self.capture.read()
        if not ret:
            print("Failed to capture frame")
            return

        result = list(self.model(frame,stream=True))
        detections = np.empty((0,5))
        for info in result:
            parameters = info.boxes
            for details in parameters:
                x1,y1,x2,y2 = details.xyxy[0]
                conf = details.conf[0]
                conf = math.ceil(conf*100)
                class_detect = int(details.cls[0])
                label = self.model.names[class_detect]
                # if label == 'can':
                x1,y1,x2,y2 = int(x1),int(y1),int(x2),int(y2)

                cv2.rectangle(frame,(x1,y1),(x2,y2),(255,0,255),5)
                cvzone.putTextRect(frame, f'{label}', [x1 + 8, y1 - 10], 2, 2, border=2)
                    # current_detections = np.array([x1, y1, x2, y2, conf])
                    # detections = np.vstack((detections, current_detections))
        
        tracker_result = self.trackers.update(detections)
        cv2.line(frame, (self.line[0],self.line[1]),(self.line[2],self.line[3]), (0, 255, 255), 5)

        for track_result in tracker_result:

            x1, y1, x2, y2, id = track_result
            x1, y1, x2, y2, id = int(x1), int(y1), int(x2), int(y2), int(id)
            w, h = x2 - x1, y2 - y1
            cx, cy = x1 + w // 2, y1 + h // 2
            

            if self.line[1] < cy < self.line[3] and self.line[2] - 10 < cx < self.line[2] + 10:
                cv2.line(frame,(self.line[0],self.line[1]),(self.line[2],self.line[3]),(0,0,255),10)
                if self.counterin.count(id) == 0:
                    self.counterin.append(id)

        cvzone.putTextRect(frame, f'Total Drinks = {len(self.counterin)}', [320, 50], thickness=4, scale=2.3, border=2)

        annotated_frame = frame
        annotated_frame = cv2.flip(annotated_frame, 0)
        # annotated_frame = cv2.flip(annotated_frame,1)

        buf = annotated_frame.tobytes()
        texture = Texture.create(size=(annotated_frame.shape[1], annotated_frame.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        self.image.texture = texture

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
class PaymentWindow(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)

class FullscreenApp(App):
    def build(self):
        Window.fullscreen = 'auto'
        Window.bind(on_key_down=self.on_key_down)
        
        # self.uart = uart_com.Uart(port="/dev/serial/by-id/usb-STMicroelectronics_STM32_Virtual_ComPort_325730633331-if00",
        #                           baudrate=115200,
        #                           timeout=1)

        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(SecondWindow(name='second_Window'))
        return sm
    
    def on_key_down(self, instance, key, *args):
        if key == 27:
            # self.uart.close()
            App.get_running_app().stop()

if __name__ == "__main__":
    FullscreenApp().run()
