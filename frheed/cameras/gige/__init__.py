# -*- coding: utf-8 -*-
"""
Connecting to GigE Vision cameras.
"""

import os
from typing import Union, Optional, List, Tuple
import time
import vimba
import cv2
import numpy as np

from frheed.cameras import CameraError, CameraObject

from vimba.c_binding import VmbCameraInfo, call_vimba_c, byref, sizeof
from vimba.error import VimbaFeatureError



_DEBUG = (__name__ == "__main__")


class GigECamera(CameraObject):
    """ 
    A class used to encapsulate a Vimba GigE camera.
    
    Attributes
    ----------
    cam : cv2.VideoCapture
    running : bool
        True if acquiring images
    camera_attributes : dictionary
        Contains all of the non-platform-specific cv2.CAP_PROP_... attributes
    camera_methods : dictionary
        Contains all of the camera methods
    
    """#### FIX THIS 
    
    @staticmethod
    def get_available_cameras() -> dict:
        """ Get available GigE cameras as a dictionary of {cam_id: name}. """
        cam_dict = {}
        with vimba.Vimba.get_instance() as vim:
            cams = vim.get_all_cameras()
            for cam_num, cam in enumerate(cams):
                cam_id = cam.get_id()
                cam_dict[cam_id] = f'GigE Camera {cam_num}'
        return(cam_dict)
    
    def __init__(self, src, vimba_camera_id = None, lock = False):
        """
        Parameters
        ----------
        """
        super().__init__()
            
        self.gige_camera_id = src
        
        self.name = f"GigE{self.gige_camera_id}"
        self.camera_type = "GigE"

            
        # Get camera attributes
        #self.camera_attributes = self.get_camera_features(self.gige_camera_id)
        
        # Other attributes which may be accessed later
          # camera is running as soon as you connect to it
        self._frame_times = []
        self.incomplete_image_count = 0
        
        
        
    
    def __enter__(self):
        super().__enter__()
        
        #Start the vimba instance
        self.vim = vimba.Vimba.get_instance()
        self.vim.__enter__()
        
        #Open the vimba camera 
        self.vim_cam = self.vim.get_camera_by_id(self.gige_camera_id)
        self.vim_cam.__enter__()
        
        ### TODO: Allow use of Mono16 Pixel format
        self.vim_cam.set_pixel_format(vimba.frame.PixelFormat.Mono12)

        self.running = True
        
        return(self)

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.vim_cam.__exit__(exc_type, exc_value, exc_traceback)
        self.vim.__exit__(exc_type, exc_value, exc_traceback)
        super().__exit__(exc_type, exc_value, exc_traceback)
        
        self._frame_times = []
        self.incomplete_image_count = 0
        self.running = False
    
    def __del__(self) -> None:
        self.__exit__(None,None,None)
        
    def __str__(self) -> str:
        return f"GigE (Id {self.gige_camera_id})"
        
        
    def get_camera_features(self, camera_id):
        """Collect the availabe camera features from the Vimba camera object"""
        with vimba.Vimba.get_instance() as vim:
            with vim.get_camera_by_id(camera_id) as cam:
                features = {}
                for feature in cam.get_all_features():
                    try:
                        value = feature.get()
                    except (AttributeError,VimbaFeatureError):
                        value = None
                    features[feature.get_name()] = value                    
        return(features)
    
    @property
    def real_fps(self) -> float:
        """ Get the real frames per second (Hz) """
        if len(self._frame_times) <= 60:
            return 0.
        else:
            return 60 / (self._frame_times[-1] - self._frame_times[-60])
    
    @property
    def width(self) -> int:
        return(self.vim_cam.Width.get())
        
    @property
    def height(self) -> int:
        return(self.vim_cam.Height.get())
    
    @property
    def shape(self) -> Tuple[int, int]:
        return((self.width, self.weight))
        
    def get_array(self):
        # Grab and retrieve the camera array
        frame = self.vim_cam.get_frame()
        array = frame.as_numpy_ndarray()
        # Store frame time for real FPS calculation
        self._frame_times.append(time.time())
        
        return(array)
    
    def disable_auto_exposure(self) -> None:### IMPLEMENT PROPERLY!!!
        pass
     #   self.CAP_PROP_EXPOSURE = 0.25
        
    def enable_auto_exposure(self) -> None:### IMPLEMENT PROPERLY!!!
        pass
     #   self.CAP_PROP_EXPOSURE = 0.75
        
    def get_info(self, name: str) -> dict:
        info = {"name": name}
        return info


if __name__ == "__main__":
    print(get_available_cameras())