# -*- coding: utf-8 -*-
"""
Widgets for selecting things, including the source camera to use.
"""

from typing import Optional, Union, List
from dataclasses import dataclass
from functools import partial

from PyQt5.QtWidgets import (
    QWidget,
    QPushButton,
    QGridLayout
    )
from PyQt5.QtCore import (
    Qt,
    pyqtSignal
    )
    
from frheed.cameras import CameraObject, CameraError, find_available_cameras
from frheed.utils import get_icon

class CameraSelection(QWidget):
    
    is_camera_selected = pyqtSignal()
    
    def __init__(self) -> None:
    
        super().__init__(None)
        
        # Check for available cameras
        cams = find_available_cameras()
        
        # Set window properties
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Window)
        self.setWindowTitle("Select Camera")
        self.setWindowIcon(get_icon("FRHEED"))
        # Set size
        self.setMinimumWidth(300)
        # Create layout
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        
        # If there are no cameras, no buttons need to be added
        if not cams:
            btn = QPushButton("No cameras found")
            btn.setEnabled(False)
            self.layout.addWidget(btn, 0, 0)
        
        # Create buttons for each camera
        for i, cam in enumerate(cams):
            btn = QPushButton(str(cam[1]))
            
            #Use partial() to make a function of no arguments
            btn.clicked.connect(partial(self._set_camera, cam[0]))
            
            self.layout.addWidget(btn, i, 0)
            
        
        self.setVisible(True)
        self.raise_()
    
    def _set_camera(self, cam:CameraObject) -> None:
        self.the_camera = cam
        
        # Hide the selection widget
        self.setVisible(False)
        
        # Emit is_camera_selected signal
        self.is_camera_selected.emit()
    
    def closeEvent(self, event) -> None:
        self.is_camera_selected.emit()
        super().closeEvent(event)

if __name__ == "__main__":
    pass
