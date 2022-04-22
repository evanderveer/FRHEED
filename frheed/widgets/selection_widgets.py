# -*- coding: utf-8 -*-
"""
Widgets for selecting things, including the source camera to use.
"""

from typing import Optional, Union, List
from dataclasses import dataclass
from enum import Enum
from functools import partial

from PyQt5.QtWidgets import (
    QWidget,
    QPushButton,
    QGridLayout,
    
    )
from PyQt5.QtCore import (
    Qt,
    pyqtSignal,
    
    )
    
from frheed.cameras import CameraObject
from frheed.cameras import CameraError
from frheed.utils import get_icon
from frheed.cameras import camera_classes
for module, cam_class in camera_classes.items():
    exec(f'from frheed.cameras.{module} import {cam_class}, get_available_cameras as get_{module}_cams')



cam_classes_list = ','.join([cam_class for cam_class in camera_classes.values()])

def select_camera(camera_widget):
    print("Selecting camera")
    camera_selection_window = CameraSelection(camera_widget)
    
    return(camera_selection_window)
    
    
def _find_available_cameras():
    # Check each camera class for availability
    usb_cams = [CameraObject(UsbCamera, src, name) 
                for src, name in get_usb_cams().items()]
    flir_cams = [CameraObject(FlirCamera, src, name)
                 for src, name in get_flir_cams().items()]
    gigE_cams = []#[CameraObject(GigECamera, src, name)
                 #for src, name in get_gige_cams().items()]
    print(get_gige_cams())
    
    return(usb_cams + flir_cams + gigE_cams)


class CameraSelection(QWidget):
    
    is_camera_selected = pyqtSignal()
    
    def __init__(self, camera_widget):
        super().__init__(None)
        print("Selection window created")
        
        # NOTE: No parent is provided so the window can be minimized to the taskbar
        # TODO: Apply global stylesheet
        
        self.camera_widget = camera_widget
        
        # Check for available cameras
        cams = _find_available_cameras()
        
        # Set window properties
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Window)
        self.setWindowTitle("Select Camera")
        self.setWindowIcon(get_icon("FRHEED"))
        
        # Set size
        self.setMinimumWidth(300)
        
        # Create layout
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        
        print("Cameras collected")
        
        # If there are no cameras, no buttons need to be added
        if not cams:
            btn = QPushButton("No cameras found")
            btn.setEnabled(False)
            self.layout.addWidget(btn, 0, 0)
        
        # Create buttons for each camera
        for i, cam in enumerate(cams):
            btn = QPushButton(cam.name)
            
            #Use partial() to make a function of no arguments
            btn.clicked.connect(partial(self._set_camera, cam))
            
            self.layout.addWidget(btn, i, 0)
            
        self.setVisible(True)
        self.raise_()
        print("Waiting for click")
    
    def _set_camera(self, cam):        
        # Initialize camera
        self.camera_widget.set_camera(cam.cam_class) ###THIS SHOULD STILL BE CHANGED!!!
        print(f"Connected to {cam.name}")
        
        # Emit is_camera_selected signal
        self.is_camera_selected.emit()
        
        # Hide the selection widget
        self.setVisible(False)
    
    

if __name__ == "__main__":
    cam_select = CameraSelection()
