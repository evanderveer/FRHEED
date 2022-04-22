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


_DEBUG = (__name__ == "__main__")


def get_available_cameras() -> vimba.camera.Camera:
    """ Get available GigE cameras as a dictionary of {cam_id: name}. """
    cam_dict = {}
    with vimba.Vimba.get_instance() as vim:
        print('Vimba started')
        print('Collecting available cameras')
        cams = vim.get_all_cameras()
        
        for cam_num, cam_id in enumerate(cams.get_id()):
            cam_dict[cam_id] = cam_num
    
    return(cam_dict)
    
    
class GigECamera:
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
    
    
    def __init__(self, vimba_camera_id = None, lock = False):
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
        super().__setattr__("camera_attributes", {})
        super().__setattr__("camera_methods", {})
        super().__setattr__("lock", lock)
        
        self.gige_camera_id = vimba_camera_id
        
        self.name = f"GigE{self.src}"
        self.camera_type = "GigE"
        
        # Initialize the camera, either by index or filepath (to video)
        if backend is not None:### IMPLEMENT PROPERLY!!!
            self.cam = cv2.VideoCapture(src, backend)
        else:
            self.cam = cv2.VideoCapture(src)
            
        # Get camera attributes
        for attr in _CAP_PROPS:### IMPLEMENT PROPERLY!!!
            self.camera_attributes[attr] = {}
            if attr in self._cap_props:
                self.camera_attributes[attr]["description"] = self._cap_props[attr]
        
        # Other attributes which may be accessed later
        self.running = True  # camera is running as soon as you connect to it
        self._frame_times = []
        self.incomplete_image_count = 0
                
    def __enter__(self) -> "UsbCamera":
        self.init()
        return self
    
    def __exit__(self, type, value, traceback) -> None:
        self.close()
        
    def __del__(self) -> None:
        self.close()
        
    def __str__(self) -> str:
        return f"GigE (Port {self.src})"
        
        
    def get_camera_features(self, camera_id):
        """Collect the availabe camera features from the Vimba camera object"""
        with vimba.Vimba.get_instance() as vim:
            with get_camera(camera_id) as cam:
                features = {}
                for feature in cam.get_all_features():
                    try:
                        value = feature.get()
                    except (AttributeError,VimbaFeatureError):
                        value = None
                    features[feature.get_name()] = value                    
        return(cam.get_all_features())

    @property
    def initialized(self) -> bool:### IMPLEMENT PROPERLY!!!
        return self.cam.isOpened()
    
    
    @property
    def real_fps(self) -> float:
        """ Get the real frames per second (Hz) """
        if len(self._frame_times) <= 60:
            return 0.
        else:
            return 60 / (self._frame_times[-1] - self._frame_times[-60])
    
    @property
    def width(self) -> int:### IMPLEMENT PROPERLY!!!
        return int(self.CAP_PROP_FRAME_WIDTH)
    
    @property
    def height(self) -> int:### IMPLEMENT PROPERLY!!!
        return int(self.CAP_PROP_FRAME_HEIGHT)
    
    @property
    def shape(self) -> Tuple[int, int]:### IMPLEMENT PROPERLY!!!
        return (self.width, self.height)
    
    def init(self):### IMPLEMENT PROPERLY!!!
        if not self.initialized:
            self.cam.open(self._src)
    
    def start(self, continuous: bool = True) -> None:### IMPLEMENT PROPERLY!!!
        # Initialize the camera
        self.init()
            
        # Begin acquisition
        self.running = True
        
    def stop(self) -> None:### IMPLEMENT PROPERLY!!!
        self._frame_times = []
        self.incomplete_image_count = 0
        self.running = False
    
    def close(self) -> None:### IMPLEMENT PROPERLY!!!
        self.stop()
        self.cam.release()
        
    def get_array(self, complete_frames_only: bool = False) -> np.ndarray:### IMPLEMENT PROPERLY!!!
        # Grab and retrieve the camera array
        is_complete, array = self.cam.read()
        
        # Increment incomplete image count if full image is not retrieved
        if not is_complete:
            self.incomplete_image_count += 1
            
        # Ensure complete image is returned if option is chosen
        if complete_frames_only and not is_complete:
            return self.get_array(complete_frames_only)
        
        # Store frame time for real FPS calculation
        self._frame_times.append(time.time())
        
        return array
    
    def disable_auto_exposure(self) -> None:### IMPLEMENT PROPERLY!!!
        self.CAP_PROP_EXPOSURE = 0.25
        
    def enable_auto_exposure(self) -> None:### IMPLEMENT PROPERLY!!!
        self.CAP_PROP_EXPOSURE = 0.75
        
    def get_info(self, name: str) -> dict:
        info = {"name": name}
        return info


if __name__ == "__main__":
    print(get_available_cameras())