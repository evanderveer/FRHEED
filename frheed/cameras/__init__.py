# -*- coding: utf-8 -*-

class CameraError(Exception):
    pass
    
camera_classes = {
        'flir': 'FlirCamera',
        'usb': 'UsbCamera',
        'gige': 'GigECamera'
        }
        
class CameraObject:
    """
    The CameraObject class acts as an abstract interface for connecting to a camera. 
    """

    def __init__(self): 
        self.gui_settings = {}

    def __init__(self):
        pass
        
    def __enter__(self):
        pass
        
    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass
    
    