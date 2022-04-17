# -*- coding: utf-8 -*-

class CameraError(Exception):
    pass
    
camera_classes = {
        'flir': 'FlirCamera',
        'usb': 'UsbCamera',
        'gige': 'GigECamera'
        }