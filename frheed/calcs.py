# -*- coding: utf-8 -*-
"""
Functions for computing values from plots.
"""

from typing import Union, Optional

import numpy as np
from scipy.signal import find_peaks

from frheed.utils import snip_lists


# Ignore numpy warnings
np.seterr("ignore")


def calc_fft(x: list, y: list) -> tuple:
    """
    Calculate the FFT of a 1D series.

    Parameters
    ----------
    x : list
        X values.
    y : list
        Y values.

    Returns
    -------
    tuple
        A tuple containing (frequency, PSD) lists. PSD is Power Spectral Density.

    """
    # Make sure data is equal lengths
    # Note: this is probably unnecessary if pulling 
    # data directly from another plot
    x, y = snip_lists(x, y)
    
    # Return if x or y is invalid
    def invalid_data(data):
        return len(data) == 0 or np.nan in data
    if any(invalid_data(d) for d in (x, y)):
        return None, None
    
    # Create evenly-spaced list of sample points 
    numsamples = len(x)
    samplespacing = (x[-1]-x[0])/numsamples
    
    # Generate array of frequencies
    try:
        freq = np.fft.rfftfreq(numsamples, d=samplespacing)
    except:
        return None, None
    
    # Convert y to float32 to avoid type conflict error in following operation
    y = np.array(y, dtype=np.float32)
    
    # Remove DC signal from the y-data
    y -= np.mean(y)
    
    # Apply Hanning filter to smooth edge discontinuities
    window = np.hanning(numsamples+1)[:-1]
    if len(y) != len(window):
        return None, None
    hann = y*window

    # Calculate real FFT
    fftdata = np.fft.rfft(hann)
    
    # Normalize FFT data & catch warnings (RuntimeError) as exceptions
    import warnings
    with warnings.catch_warnings():
        warnings.filterwarnings("error")
        try:
            psd = abs(fftdata)**2/(np.abs(hann)**2).sum()
            psd = (psd*2)**0.5
            
        except Warning:
            return None, None
    
    # Sometimes the arrays can become different lengths and throw errors
    freq, psd = snip_lists(freq, psd)
    
    return (freq, psd)

def apply_cutoffs(
        x: list, 
        y: list, 
        minval: Optional[float] = None, 
        maxval: Optional[float] = None
        ) -> tuple:
    """ Return data that falls between a certain range. Pass None to use min or max. """
    
    # Return if x or y is empty
    if len(x) + len(y) == 0:
        return (x, y)
    x, y = map(np.array, (x, y))
    minval = minval or min(x)
    maxval = maxval or max(x)
    orig_x = x.copy()
    mask = (orig_x >= minval) & (orig_x <= maxval)
    return (x[mask], y[mask])

def detect_peaks(
        x: Union[list, tuple, np.ndarray],
        y: Union[list, tuple, np.ndarray],
        min_freq: Optional[float] = 0.0
        ) -> list:
    
    # Catch numpy RuntimeWarning as exceptions
    import warnings
    with warnings.catch_warnings():
        warnings.filterwarnings("error")
        
        try:
            # Filter to minimum frequency
            x, y = apply_cutoffs(x=x, y=y, minval=min_freq)
            
            # Height
            height = max(np.median(y) + 3*np.std(y), 1.5)
            
            # Threshold (vertical distance to neighbors)
            threshold = None
            
            # Distance between peaks (# of indices)
            distance = 50
            
            # Prominence
            prominence = None
            
            # Find peaks
            peak_indices, props = find_peaks(
                                        y, 
                                        height = height,
                                        threshold = threshold,
                                        distance = distance,
                                        prominence = prominence
                                        )
            
            # Get corresponding x-coordinates
            return [x[idx] for idx in peak_indices]
        
        except Warning:
            return


if __name__ == "__main__":
    pass
