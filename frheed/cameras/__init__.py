# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod

class CameraError(Exception):
    pass
    
def find_available_cameras():
    # Find available camera classes which inherit from CameraObject
    cameras = []
    for the_class in CameraObject.__subclasses__():
        for src, name in the_class.get_available_cameras().items():
            cameras.append((the_class(src), name))
    return(cameras)
    
class CameraObject(ABC):
    """
    The CameraObject class acts as an abstract interface for connecting to a camera. 
    """

    def __init__(self): 
        self.gui_settings = {}
        
    def __enter__(self):
        pass
        
    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass
    
    
    @staticmethod
    @abstractmethod
    def get_available_cameras() -> dict:
        pass
    