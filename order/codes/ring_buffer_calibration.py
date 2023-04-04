import numpy as np
import matplotlib.pyplot as plt

###
### The idea is change the gain, calculate the similarity between the two spectras
### that should be a concave function so we search for the maximum
###

def ring_buffer_calibration(roach_control, steps):
    """
    roach_control:  
    steps:  how many steps try before keeping a result
    """
    

