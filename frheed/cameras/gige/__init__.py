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

from frheed.cameras import CameraError

from vimba.c_binding import VmbCameraInfo, call_vimba_c, byref, sizeof
from vimba.error import VimbaFeatureError


_DEBUG = (__name__ == "__main__")


def get_available_cameras() -> vimba.camera.Camera:
    """ Get available GigE cameras as a dictionary of {cam_id: name}. """
    cam_dict = {}
    with vimba.Vimba.get_instance() as vim:
        print('Vimba started')
        print('Collecting available cameras')
        cams = vim.get_all_cameras()
        cams_list = []
        for cam_num, cam in enumerate(cams):
            cam_id = cam.get_id()
            cam_info = VmbCameraInfo()
            call_vimba_c('VmbCameraInfoQuery', cam_id.encode('utf-8'), byref(cam_info), sizeof(cam_info))
            cams_list.append((cam_info, cam_num))
    return(cams_list)
    
    
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
    
    """#### FIX THIS !!!
    
    
    def __init__(self, src, vimba_camera_id = None, lock = False):
        """
        Parameters
        ----------
        vimba_camera : vimba.camera.Camera
            Camera object
        lock : bool, optional
            If True, attribute access is locked down; after the camera is
            initialized, attempts to set new attributes will raise an error. 
            The default is True.
        """
        super().__init__(src)
            
        self.gige_camera_id = self.get_id()
        
        self.name = f"GigE{self.gige_camera_id}"
        self.camera_type = "GigE"

            
        # Get camera attributes
        self.camera_attributes = self.get_camera_features(self.gige_camera_id)
        
        # Other attributes which may be accessed later
        self.running = True  # camera is running as soon as you connect to it
        self._frame_times = []
        self.incomplete_image_count = 0
                
    
    def __enter__(self):
        super().__enter__(self)

    def __exit__(self, exc_type, exc_value, exc_traceback):
        super().__exit__(self, exc_type, exc_value, exc_traceback)
    
    def __del__(self) -> None:
        self.close()
        
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
    def initialized(self) -> bool:### IMPLEMENT PROPERLY!!!
        #return self.cam.isOpened()
        pass
    
    @property
    def real_fps(self) -> float:
        """ Get the real frames per second (Hz) """
        if len(self._frame_times) <= 60:
            return 0.
        else:
            return 60 / (self._frame_times[-1] - self._frame_times[-60])
    
    @property
    def width(self) -> int:### IMPLEMENT PROPERLY!!!
        return(self.Width)
        
    @property
    def height(self) -> int:### IMPLEMENT PROPERLY!!!
        return(self.Height)
    
    @property
    def shape(self) -> Tuple[int, int]:### IMPLEMENT PROPERLY!!!
        return((self.Width, self.Height))
        
    def init(self):### IMPLEMENT PROPERLY!!!
        pass
        if not self.initialized:
            self.__enter__()
    
    def start(self, continuous: bool = True) -> None:### IMPLEMENT PROPERLY!!!
        # Initialize the camera
        self.init()
            
        # Begin acquisition
        self.running = True
        
    def stop(self) -> None:### IMPLEMENT PROPERLY!!!
        self.__exit__(None,None,None)
        self._frame_times = []
        self.incomplete_image_count = 0
        self.running = False
    
    def close(self) -> None:### IMPLEMENT PROPERLY!!!
        self.stop()
        #self.cam.release()
        
    def get_array(self, complete_frames_only: bool = False) -> np.ndarray:### IMPLEMENT PROPERLY!!!
        
        # Grab and retrieve the camera array
        array = self.cam.get_frame().as_opencv_image()
        
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