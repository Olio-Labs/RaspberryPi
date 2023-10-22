from ast import Try
from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QApplication, QWidget
from picamera2 import Picamera2
from PyQt5.QtGui import QImage,QPixmap, QPainter, QColor, QFont
from PyQt5.QtCore import QThread
import RPi.GPIO as gp
import time
import os
from vidgear import gears
from libcamera import controls
import cv2
import numpy as np


width = 640
height = 480
FPS = 90 
time_to_run = 10

adapter_info = {  
    "A" : {   
        "i2c_cmd":"i2cset -y 10 0x70 0x00 0x04",
        "gpio_sta":[0,0,1],
        }, 
    "B" : {
        "i2c_cmd":"i2cset -y 10 0x70 0x00 0x05",
        "gpio_sta":[1,0,1],
        },
    "C" : {
        "i2c_cmd":"i2cset -y 10 0x70 0x00 0x06",
        "gpio_sta":[0,1,0],
        },
    #"D" : {
     #   "i2c_cmd":"i2cset -y 10 0x70 0x00 0x07",
     #   "gpio_sta":[1,1,0],
    #}
}

gp.setwarnings(False)
gp.setmode(gp.BOARD)
gp.setup(7, gp.OUT)
gp.setup(11, gp.OUT)
gp.setup(12, gp.OUT)

def select_channel(index):
    channel_info = adapter_info.get(index)
    if channel_info == None:
        print("Can't get this info")
    gpio_sta = channel_info["gpio_sta"] # gpio write
    gp.output(7, gpio_sta[0])
    gp.output(11, gpio_sta[1])
    gp.output(12, gpio_sta[2])

def init_i2c(index):
    channel_info = adapter_info.get(index)
    os.system(channel_info["i2c_cmd"]) # i2c write
    
    
    
def run():
    global picam2
    # picam2 = Picamera2()
    # picam2.configure( picam2.still_configuration(main={"size": (320, 240),"format": "BGR888"},buffer_count=1))

    
    
    flag = False

    for item in {"A", "B", "C"}: #,"B","C","D"}:
        try:
            select_channel(item)
            init_i2c(item)
            time.sleep(0.5) 
            if flag == False:
                flag = True
            else :
                picam2.close()
                # time.sleep(0.5) 
            print("init1 "+ item)
            picam2 = Picamera2()
            picam2.configure(picam2.create_still_configuration(main={"size": (640, 480),"format": "BGR888"},buffer_count=2)) 
            
            #config = picam2.create_video_configuration(main={"size": (width, height),
             #                                                  "format": "YUV420"}, 
              #                                           raw={"size": (width,height)}, # can be spoofed to a higher resolution for some cameras
               #                                          encode="main",
                #                                         controls={
                 #                                                # ~ "AfMode": self.controls.AfModeEnum.Manual, 
                  #                                               # ~ "LensPosition": 0,
                   #                                              "FrameRate" : FPS,
                    #                                             "FrameDurationLimits": (1000000 / FPS, 1000000 / FPS),
                     #                                            "NoiseReductionMode" : controls.draft.NoiseReductionModeEnum.Fast,
                      #                                           },
                       #                                          )  
            # picam2.configure(config)
            
            picam2.start()
            time.sleep(2)
            picam2.capture_array(wait=False)
            time.sleep(0.1)
            print('initiated camera', item)
        except Exception as e:
            print("except: "+str(e))
    
    print('start video writer')
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    writer = cv2.VideoWriter('output.avi', fourcc, FPS, (width, height))
    print('writer initiated')
    
    array = np.zeros([10*60, height, width, 3], dtype='uint8')
    

    t0 = time.time()
    i = 0
    j = 0
    
    while time.time() - t0 < time_to_run:
        
        for item in {"A", "B", "C"}: #,"B","C","D"}:
            select_channel(item)
            time.sleep(0.02)
            try:
                frame = picam2.capture_array()
                #print(frame.shape)
                #print(type(frame[0,0,0]))
                array[i,:,:,:] = frame
                j += 1
                #writer.write(frame)
                #break
        #break
               
                
                
            except Exception as e:
                print("capture_buffer: "+ str(e))
                
        print(str(i), str(round(time.time() - t0,2)))
        i += 1
        
    print('done')
                
    writer.release()
    picam2.close()
    
    
if __name__ == "__main__":
    run()
