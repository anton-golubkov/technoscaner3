#!/usr/bin/python
# -*- coding: utf-8 -*-

import cv
import math

class ChessboardAnalyzer:
    """ 
    Image analyzer class 
    
    Analyzer find chessboard in given image
    """
    
    def __init__ (self):
        self._prev_point = (0, 0)
        return                    
    
    
    def findObject(self, image):
        """ 
        Find object coordinates in image
        
        Return (x, y) coordinates of objects if find, 
        otherwise previous matching point
        """ 
        
        corners = cv.FindChessboardCorners(image, (3, 5)) # cv.CV_CALIB_CB_ADAPTIVE_THRESH)
        if corners[0] == 1:
            self._prev_point = corners[1][7]
            return corners[1][7]
        else:
            return self._prev_point
        
        
