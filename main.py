from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import (QApplication,QFileDialog, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QSlider,QVBoxLayout, QWidget)
from PyQt6.QtGui import QDesktopServices, QImage, QPixmap, QGuiApplication
from math import gcd

# https://doc.qt.io/qt-6/opengl-changes-qt6.html
#from PyQt6.QtOpenGLWidgets import QOpenGLWidget

import numpy as np
import cv2
import json, pdb


class bboxChecker(QWidget):
    def __init__(self, parent=None):
        super(bboxChecker, self).__init__(parent)
        self.idx = 0
        self.w = 640 #1280
        self.h = 360 #720
        self.frameCount = 0
        self.cap = None
        self.setWindowTitle('Bounding Box Checker')
        
        ## PyQt6 GUI
        self.layout_main = QVBoxLayout()

        self.widget_display = QLabel()
        self.layout_main.addWidget(self.widget_display)

        self.widget_slider = QSlider(Qt.Orientation.Horizontal)
        self.layout_main.addWidget(self.widget_slider)

        self.layout_control = QHBoxLayout()
        self.btn_load = QPushButton("Load")
        self.label_frame = QLabel("/")
        self.btn_left = QPushButton("<-")
        self.btn_right = QPushButton("->")
        self.layout_control.addWidget(self.btn_load)
        self.layout_control.addWidget(self.label_frame)
        self.layout_control.addWidget(self.btn_left)
        self.layout_control.addWidget(self.btn_right)
        self.layout_main.addLayout(self.layout_control)
        
        
        self.label_path = QLabel(".")
        self.layout_main.addWidget(self.label_path)

        self.setLayout(self.layout_main)

        self.btn_load.pressed.connect(self.showDialog)
        
        # self.widget_display.setFixedSize(QSize(self.w,self.h))
        self.widget_display.resize(QSize(self.w,self.h))
        self.label_frame.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.widget_slider.sliderMoved.connect(self.display)
        self.btn_left.released.connect(self.flag_left)
        self.btn_right.released.connect(self.flag_right)
        
        self.center()
        
    
    def center(self): 
        cp = QGuiApplication.primaryScreen().availableGeometry().center()
        x = cp.x() - self.w/2
        y = cp.y() - self.h*4/7
        self.move(x, y)
    
    def flag_left(self):
        flag = -1
        idx = self.widget_slider.value() + flag
        self.widget_slider.setValue(idx)
        self.display(idx)
    
    def flag_right(self):
        flag = 1
        idx = self.widget_slider.value() + flag
        self.widget_slider.setValue(idx)
        self.display(idx)
    
    def showDialog(self):
        path_mp4 = QFileDialog.getOpenFileName(self, 'Open file', './', "mp4 (*.mp4)")
        # (path_mp4, type)
        path_mp4 = str(path_mp4[0])
        self.path_mp4 = path_mp4
        path_json = path_mp4.replace('/video/', '/json/').replace('.mp4', '.json')
        self.path_json = path_json
        
        if path_mp4 == "" :
            pass
        else :
            self.label_path.setText(path_mp4)
            self.load(path_mp4, path_json)

    def load(self,path_mp4, path_json):
        if self.cap is not None:
            self.cap.release()
        self.cap = cv2.VideoCapture(path_mp4)
        self.frameCount = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.frameWidth = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frameHeight = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        with open(path_json, 'r') as f:
            data_json = json.load(f)
        self.json_Face = data_json['Face_bounding_box']['xtl_ytl_xbr_ybr']
        self.json_Lip = data_json['Lip_bounding_box']['xtl_ytl_xbr_ybr']
        
        self.widget_slider.setRange(0,self.frameCount)
        
        self.display(0)

    def display(self,idx): # bounding box
        if self.frameCount <=0:
            return
        if idx < 0 or idx >= self.frameCount:
            return

        self.cap.set(cv2.CAP_PROP_POS_FRAMES,idx)
        ret, tmp = self.cap.read()
        face = self.json_Face[idx]
        lip = self.json_Lip[idx]
               
        if not ret :
            return

        cv2.rectangle(tmp, (face[1],face[0]), (face[3],face[2]), (255,0,0), 2) # Face - Blue
        cv2.rectangle(tmp, (lip[1],lip[0]), (lip[3],lip[2]), (0,0,255), 2) # Lip - Red
        
        # tmp = cv2.resize(tmp,(self.w,self.h), interpolation = cv2.INTER_LINEAR)
        # qImg = QImage(tmp, self.w, self.h, self.w*3, QImage.Format.Format_BGR888)
        
        [size_h, size_w, rgb] = tmp.shape
        
        size_h = int(size_h/3)
        size_w = int(size_w/3)
        
        tmp = cv2.resize(tmp,(size_w,size_h), interpolation = cv2.INTER_LINEAR)
        qImg = QImage(tmp, size_w, size_h, size_w*3, QImage.Format.Format_BGR888)
        
        pixmap01 = QPixmap.fromImage(qImg)
        pixmap_image = QPixmap(pixmap01)
        self.widget_display.setPixmap(pixmap_image)

        self.label_frame.setText(str(idx)+" / "+str(self.frameCount))

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    gallery = bboxChecker()
    gallery.show()
    sys.exit(app.exec()) 

