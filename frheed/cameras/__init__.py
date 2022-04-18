# -*- coding: utf-8 -*-

class CameraError(Exception):
    pass
    
camera_classes = {
        'flir': 'FlirCamera',
        'usb': 'UsbCamera',
        'gige': 'GigECamera'
        }
        
class CameraObject:

    def __init__(self, cam_class, src, name):
        self.cam_class = cam_class(src)
        self.name = name