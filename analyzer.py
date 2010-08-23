#!/usr/bin/python
# -*- coding: utf-8 -*-

import cv
import math

class Analyzer:
    """ 
    Image analyzer class 
    
    Analyzer find point in given image, that matching the template
    """
    
    def __init__ (self, template):
               
        self._trimg     = None
        self._grimg     = None
        self._result    = None
        self._thresh    = None
        self._template  = cv.CloneImage(template)
        
        self._prevMatchPoint = (0, 0)

        
        # Grow when no matching point found
        self._inertiaPenalty = 0
        
        # Size of analyzed image 
        # when size is changed we need recreate temporary images
        self._currentImageSize = (0, 0)
    
    
    def findObject(self, image):
        """ 
        Find object coordinates in image
        
        Return (x, y) coordinates of objects if find, 
        otherwise previous matching point
        """ 
        matchPoints = self._findTemplateMatchPoints(image)
        if len(matchPoints) > 0:
            matchPoint = self._determinePoint(self._prevMatchPoint, matchPoints, 10.0)
            self._prevMatchPoint = matchPoint
        return self._prevMatchPoint
        
        
        
    
    def _createTempImages(self, imageSize):
        """ Create images, necessary for recognition algorithm """
        
        self._trimg = cv.CreateImage(imageSize, cv.IPL_DEPTH_8U, 1)
        self._grimg = cv.CreateImage(imageSize, cv.IPL_DEPTH_8U, 1)
        rwidth = imageSize[0] - self._template.width + 1;
        rheight = imageSize[1] - self._template.height + 1;
        self._result = cv.CreateImage((rwidth, rheight), cv.IPL_DEPTH_32F, 1)
        self._thresh = cv.CreateImage(cv.GetSize(self._result), cv.IPL_DEPTH_8U, 1)
        
        
        
    def _findTemplateMatchPoints(self, srcimg):
        """ 
        Find all points in srcimg that matches self._template 
        
        Return list of points [(x1, y1), (x2, y2), ...]
        """
        
        """ Create internal memory storage"""
        storage = cv.CreateMemStorage(0)
        
        # If size of analyzed image changes or temp images not created yet
        # we need to create temporary images
        if ( self._currentImageSize != cv.GetSize(srcimg) ) or ( self._trimg == None):
           self._createTempImages( cv.GetSize(srcimg) )
        
        cv.CvtColor(srcimg, self._grimg, cv.CV_RGB2GRAY)    
        cv.Threshold(self._grimg, self._trimg, 90, 255, cv.CV_THRESH_BINARY_INV);

        contours = cv.FindContours(self._trimg, storage)
        if len(contours) > 0:
            cv.Zero(self._grimg)
            contour = contours
            while contour != None:
                area = cv.ContourArea(contour)
                if area > 300:
                    cv.DrawContours(self._grimg, contour, (255, 255, 255), (255, 255, 255), -1)            
                contour = contour.h_next()
        cv.MatchTemplate( self._grimg, self._template, self._result, cv.CV_TM_CCORR_NORMED)
        cv.Normalize(self._result, self._result, 1, 0, cv.CV_MINMAX)
        cv.Pow(self._result, self._result, 3)

        
        cv.ConvertScale( self._result, self._thresh, 255)
        cv.Threshold( self._thresh, self._thresh, 230, 255, cv.CV_THRESH_BINARY);
        contours = cv.FindContours( self._thresh, storage)
        match_points = []
        if len(contours) > 0:
            contour = contours
            while contour != None:
                brect = cv.BoundingRect(contour)
                match_points.append((brect[0] + self._template.width/2, brect[1]+self._template.height/2))
                contour = contour.h_next()
        """ Release internal memory storage"""

        del contours
        return match_points


    def _distance(self, p1, p2):
        """ Calculate distance between two points """
        
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
    
    
    def _trimPointsByDistance(self, originPoint, points, trimDistance):
        """ 
        Find points laying close to originPoint
        
        Returns set of points, that laying in circle 
        with radius trimDistance and center in originPoint
        """
    
        retPoints = []
        for point in points:
            if self._distance(originPoint, point) <= trimDistance:
                retPoints.append(point)
        return retPoints
    
    
    def _nearestPoint(self, originPoint, points):
        """ Find point closest to originPoint in set of points"""
        
        dstList = []
        for point in points:
            dstList.append( self._distance(originPoint, point))

        iMax = 0
        for i, dst in enumerate(dstList):
            if dstList[iMax] < dst:
                iMax = i
        return points[iMax]
        

    def _determinePoint(self, prevPoint, matchPoints, inertiaDistance):
        """ Select best matching point from matched points set
        
            Algorithm using inertiaPenalty - when new point laying
            far from previous matching point returning previous point
            and inertiaPenalty increased, 
            so in next time area of allowed points increased
        """
        
        trPoints = self._trimPointsByDistance(prevPoint, matchPoints, inertiaDistance + self._inertiaPenalty)
        if len(trPoints) > 0:
            self._inertiaPenalty = 0
            return self._nearestPoint(prevPoint, trPoints)
        else:
            # Nearest point not found, increase inertia penalty and return previous point
            self._inertiaPenalty = self._inertiaPenalty + inertiaDistance
            return prevPoint


