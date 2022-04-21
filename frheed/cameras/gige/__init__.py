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


def get_available_cameras() -> dict:
    """ Get available GigE cameras as a dictionary of {source: name}. """
    cam_dict = {}
    with vimba.Vimba.get_instance() as vim:
        cams = vim.get_all_cameras()
        
        for cam_num, cam_src in enumerate(cams):
            cam_dict[cam_src] = cam_num
    
    return(available)
    
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
    
    
    def __init__(self, src = 0, lock = False):
        """
        Parameters
        ----------
        src : Union[int, str], optional
            Camera source as an index or path to video file. The default is 0.
        lock : bool, optional
            If True, attribute access is locked down; after the camera is
            initialized, attempts to set new attributes will raise an error. 
            The default is True.
        backend : Optional[int], optional
            Camera backend. The default is cv2.CAP_DSHOW.
        """
        super().__setattr__("camera_attributes", {})
        super().__setattr__("camera_methods", {})
        super().__setattr__("lock", lock)
        
        
        self._src_type = type(src)
        self._src = src
        
        self.name = f"GigE{self._src}"
        self.camera_type = "GigE"
        
        # Initialize the camera, either by index or filepath (to video)
        if backend is not None:
            self.cam = cv2.VideoCapture(src, backend)
        else:
            self.cam = cv2.VideoCapture(src)
            
        # Get camera attributes
        for attr in _CAP_PROPS:
            self.camera_attributes[attr] = {}
            if attr in self._cap_props:
                self.camera_attributes[attr]["description"] = self._cap_props[attr]
        
        # Other attributes which may be accessed later
        self.running = True  # camera is running as soon as you connect to it
        self._frame_times = []
        self.incomplete_image_count = 0
        
    def __getattr__(self, attr: str) -> object:
        # Add this in so @property decorator works as expected
        if attr in self.__dict__:
            return self.__dict__[attr]
        
        elif attr in self.camera_attributes:
            propId = getattr(cv2, attr, None)
            if propId is None:
                raise AttributeError(f"{attr} is not a valid propId")
            return self.cam.get(propId)
        
        else:
            raise AttributeError(attr)
            
    def __setattr__(self, attr: str, val: object) -> None:
        if attr in self.camera_attributes:
            propId = getattr(cv2, attr, None)
            if propId is None:
                raise AttributeError(f"Unknown propId '{attr}'")
                
            # In order to change CAP_PROP_EXPOSURE, it has to be set to 0.25
            # first in order to enable manual exposure
            # https://github.com/opencv/opencv/issues/9738#issuecomment-346584044
            if propId in ["CAP_PROP_EXPOSURE"]:
                self.cam.set(propId, 0.25)
                
            success = self.cam.set(propId, val)
            result = "succeeded" if success else "failed"
            if _DEBUG or not success:
                print(f"Setting {attr} to {val} {result}")
            
        else:
            if attr == "__class__":
                super().__setattr__(attr, val)
            elif attr not in self.__dict__ and self.lock and self.initialized:
                raise CameraError(f"Unknown property '{attr}'")
            else:
                super().__setattr__(attr, val)
        
    def __enter__(self) -> "UsbCamera":
        self.init()
        return self
    
    def __exit__(self, type, value, traceback) -> None:
        self.close()
        
    def __del__(self) -> None:
        self.close()
        
    def __str__(self) -> str:
        return f"GigE (Port {self._src})"

    @property
    def initialized(self) -> bool:
        return self.cam.isOpened()
    
    
    @property
    def real_fps(self) -> float:
        """ Get the real frames per second (Hz) """
        
        # When not enough frames have been captured
        if len(self._frame_times) <= 1:
            return 0.
        
        # When fewer than 60 frames have been captured in this acquisition
        elif len(self._frame_times) < 60:
            dt = (self._frame_times[-1] - self._frame_times[0])
            return len(self._frame_times) / max(dt, 1)
        
        # Return the average frame time of the last 60 frames
        else:
            return 60 / (self._frame_times[-1] - self._frame_times[-60])
    
    @property
    def width(self) -> int:
        return int(self.CAP_PROP_FRAME_WIDTH)
    
    @property
    def height(self) -> int:
        return int(self.CAP_PROP_FRAME_HEIGHT)
    
    @property
    def shape(self) -> Tuple[int, int]:
        return (self.width, self.height)
    
    def init(self):
        if not self.initialized:
            self.cam.open(self._src)
    
    def start(self, continuous: bool = True) -> None:
        # Initialize the camera
        self.init()
            
        # Begin acquisition
        self.running = True
        
    def stop(self) -> None:
        self._frame_times = []
        self.incomplete_image_count = 0
        self.running = False
    
    def close(self) -> None:
        self.stop()
        self.cam.release()
        
    def get_array(self, complete_frames_only: bool = False) -> np.ndarray:
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
    
    def disable_auto_exposure(self) -> None:
        self.CAP_PROP_EXPOSURE = 0.25
        
    def enable_auto_exposure(self) -> None:
        self.CAP_PROP_EXPOSURE = 0.75
        
    def get_info(self, name: str) -> dict:
        info = {"name": name}
        return info


if __name__ == "__main__":
    pass