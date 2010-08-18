#!/usr/bin/python
# -*- coding: utf-8 -*-


import math
import MySQLdb
import cv
import sys
from PyQt4 import QtGui, QtCore
from mainform import Ui_Form
from PIL import Image
import StringIO


### Global variables ###

# Application main form
mainForm = None

# Database connection
connection = None

# Video-frames storage
videoStorage = None

# Template image, used to find objects on image
templateContour = None

# Timer interval, ms
timerInterval = 10


# Recognized results list [(time, value, frame_id), ...]
results = []

class DbFrameStorage():
    def __init__(self, connection):
        self._connection = connection
        self._id_cursor = self._connection.cursor()
        self._frame_cursor = self._connection.cursor()
        self._current_frame = 0
        self._id = []
        self._time = []
        
    def open(self, expId, camId):
        self._current_frame = 0
        self._id_cursor.execute("SELECT id, time from video where experiment_id = %s and sensor_id = %s", (expId, camId) )
        self._id = []
        self._time = []
        self._expId = expId
        self._camId = camId
        for row in self._id_cursor.fetchall():
            self._id.append(row[0])
            self._time.append(row[1])
            
    def getFrameCount(self):
        return len(self._id)
    
    def getFrameId(self, frameNum):
        return self._id[frameNum]
    
    def getFrameTime(self, frameNum):
        return self._time[frameNum]
    
    def getExpId(self):
        return self._expId
    
    def getCamId(self):
        return self._camId
        
    def getFrame(self, frameNum):
        """ Returns frame from database in QPixmap and OpenCV IPL_Image format as (QPixmap, IPL_Image)"""
        
        self._frame_cursor.execute("SELECT frame from video where id = %s", (self._id[frameNum]) )
        frame = self._frame_cursor.fetchone()[0]
        if frame != None:
            self._current_frame = frameNum
            # Create IPL_Image object from image data
            strfile = StringIO.StringIO(frame)
            pil = Image.open(strfile)
            ipl_image = cv.CreateImage(pil.size, cv.IPL_DEPTH_8U, 3)     # OpenCV image
            cv.SetData(ipl_image, pil.tostring(), pil.size[0]*3)
            cv.CvtColor(ipl_image, ipl_image, cv.CV_RGB2BGR)
            
            # Create QPixmap from image data
            qpixmap = QtGui.QPixmap()
            qpixmap.loadFromData(frame)

            return (qpixmap, ipl_image)
        else:
            self._current_frame = 0
            return (None, None)


	
def load_template():
    global mainForm
    global templateContour
    fileName = QtGui.QFileDialog.getOpenFileName(mainForm, 
                                                 "Select template"
                                                 ".",
                                                 "Images (*.png *.xpm *.jpg *.bmp)")
    if len(fileName) > 0:
        templateContour = cv.LoadImage( unicode(fileName).encode("utf-8") , cv.CV_LOAD_IMAGE_GRAYSCALE)
        templatePixmap = QtGui.QPixmap()
        templatePixmap.load(fileName)
        mainForm.ui.templateImage.setPixmap(templatePixmap)


    



    


def init_exp():
    global connection
    global mainForm
    cursor = connection.cursor()
    cursor.execute("SELECT id, time from experiment")
    for row in cursor.fetchall():
           mainForm.ui.experimentList.addItem(str(row[0]) + ' - ' + row[1][0:17], row[0])
    
def update_cam_list(experimentIndex):
    global connection
    global mainForm
    expId = mainForm.ui.experimentList.itemData(experimentIndex).toUInt()[0]
    mainForm.ui.cameraList.clear()
    cursor = connection.cursor()
    cursor.execute("SELECT experiment_id, sensor_directory.id, sensor_directory.name FROM sensors, sensor_directory WHERE sensor_id = sensor_directory.id AND type='IP-CAM' AND experiment_id=%s", (expId))
    for row in cursor.fetchall():
           mainForm.ui.cameraList.addItem(row[2], row[1])
    
def open_experiment():
    global mainForm
    global connection
    global videoStorage
    global results
    # Clear results
    results = []
    expId = mainForm.ui.experimentList.itemData( mainForm.ui.experimentList.currentIndex()).toUInt()[0]
    camId = mainForm.ui.cameraList.itemData( mainForm.ui.cameraList.currentIndex()).toUInt()[0]
    videoStorage.open(expId, camId)
    frameCount = videoStorage.getFrameCount()
    if frameCount > 0:
        mainForm.ui.timeSlider.setEnabled(True)
        mainForm.ui.timeSlider.setMaximum(frameCount-1)
        mainForm.ui.timeSlider.setValue(0)
    else:
        mainForm.ui.timeSlider.setMaximum(0)
        mainForm.ui.timeSlider.setEnabled(False)
        




def findContourMatch(srcimg, template):

	storage = cv.CreateMemStorage(0)
	trimg = cv.CreateImage(cv.GetSize(srcimg), cv.IPL_DEPTH_8U, 1)
	grimg = cv.CreateImage(cv.GetSize(srcimg), cv.IPL_DEPTH_8U, 1)
	cv.CvtColor(srcimg, grimg, cv.CV_RGB2GRAY)	

	cv.Threshold(grimg,trimg, 90, 255, cv.CV_THRESH_BINARY_INV);

	contours = cv.FindContours(trimg, storage)
	if len(contours) > 0:
		cv.Zero(grimg)
		contour = contours
		while contour != None:
			area = cv.ContourArea(contour)
			if area > 300:
				cv.DrawContours(grimg, contour, (255, 255, 255), (255, 255, 255), -1)			
			contour = contour.h_next()
	rwidth = srcimg.width - template.width + 1;
	rheight = srcimg.height - template.height + 1;

	result = cv.CreateImage((rwidth, rheight), cv.IPL_DEPTH_32F, 1)
	cv.MatchTemplate( grimg, template, result, cv.CV_TM_CCORR_NORMED)
	cv.Normalize(result, result, 1, 0, cv.CV_MINMAX)
	cv.Pow(result, result, 3)

	thresh = cv.CreateImage(cv.GetSize(result), cv.IPL_DEPTH_8U, 1)
	cv.ConvertScale(result, thresh, 255)
	cv.Threshold(thresh, thresh, 230, 255, cv.CV_THRESH_BINARY);
	contours = cv.FindContours(thresh, storage)
	match_points = []
	if len(contours) > 0:
		contour = contours
		while contour != None:
			brect = cv.BoundingRect(contour)
			match_points.append((brect[0] + template.width/2, brect[1]+template.height/2 + -30))
			contour = contour.h_next()
	return match_points


def distance(p1, p2):
	return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
	
def trimPointsByDistance(originPoint, points, trimDistance):
	retPoints = []
	for point in points:
		if distance(originPoint, point) <= trimDistance:
			retPoints.append(point)
	return retPoints
	
def nearestPoint(originPoint, points):
	dstList = []
	for point in points:
		dstList.append(distance(originPoint, point))

	iMax = 0
	for i, dst in enumerate(dstList):
		if dstList[iMax] < dst:
			iMax = i
	return points[iMax]
		

# Растет, когда следующая точка не попадает в область инерции
inertionPenalty = 0
def determinePoint(prevPoint, matchPoints, inertionDistance):
	global inertionPenalty
	trPoints = trimPointsByDistance(prevPoint, matchPoints, inertionDistance + inertionPenalty)
	if len(trPoints) > 0:
		inertionPenalty = 0
		return nearestPoint(prevPoint, trPoints)
	else:
	# Ближайших точек нет, увеличиваем штраф инерции и оставляем текущую точку в качестве результата
		inertionPenalty = inertionPenalty + inertionDistance
		return prevPoint
	

matchPoint = (0, 0)
def change_frame(frameNum):
    global mainForm
    global videoStorage
    global matchPoint
    global templateContour
    global results
    
    frame = videoStorage.getFrame(frameNum)
    pixmap = frame[0]
    ipl_image = frame[1]
   
    
    matchPoints = findContourMatch(ipl_image, templateContour)
    if len(matchPoints) > 0:
        matchPoint = determinePoint(matchPoint, matchPoints, 10.0)
    
    # Add y coordinate of point to results
    results.append(  (  videoStorage.getFrameTime(frameNum), 
                        pixmap.height() - matchPoint[1], 
                        videoStorage.getFrameId(frameNum) )  )

    painter = QtGui.QPainter()
    painter.begin(pixmap)
#    painter.setPen( red )
    painter.drawEllipse( matchPoint[0], matchPoint[1], 20,20 )
    painter.end()
    mainForm.ui.image.setPixmap(pixmap)

def timer_tick():
    global mainForm
    mainForm.ui.timeSlider.setValue(mainForm.ui.timeSlider.value() + 1)

def play_video():
    global mainForm
    global timerInterval
    mainForm.timer.start(timerInterval)

def pause_video():
    global mainForm
    mainForm.timer.stop()

def save_results():
    global results
    global connection
    global videoStorage
    
    cursor = connection.cursor()
    
    cursor.execute("INSERT INTO results_directory (type, description, experiment_id, analizator_id, sensor_id) VALUES( %s, %s, %s, %s, %s);", ("h", "h ts3", videoStorage.getExpId(), 0, videoStorage.getCamId()) )
    
    cursor.execute("SELECT LAST_INSERT_ID()")
    resultId = cursor.fetchone()[0]
    
    for i, item in enumerate(results):
        cursor.execute("INSERT INTO results (time, value, frame_id, distance_from_origin, result_id) VALUES (%s, %s, %s, %s, %s);", 
                       (item[0], item[1], item[2], i, resultId) )

class MainForm(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.timer = QtCore.QTimer()

        QtCore.QObject.connect(self.ui.experimentList, QtCore.SIGNAL("currentIndexChanged(int)"),
            update_cam_list)
        QtCore.QObject.connect(self.ui.openButton, QtCore.SIGNAL("clicked()"),
            open_experiment)
        QtCore.QObject.connect(self.ui.selectTemplateButton, QtCore.SIGNAL("clicked()"),
            load_template)
        QtCore.QObject.connect(self.ui.timeSlider, QtCore.SIGNAL("valueChanged(int)"),
            change_frame)
        QtCore.QObject.connect(self.timer, QtCore.SIGNAL("timeout()"),
            timer_tick)
        QtCore.QObject.connect(self.ui.playButton, QtCore.SIGNAL("clicked()"),
            play_video)
        QtCore.QObject.connect(self.ui.pauseButton, QtCore.SIGNAL("clicked()"),
            pause_video)
        QtCore.QObject.connect(self.ui.saveResultsButton, QtCore.SIGNAL("clicked()"),
            save_results)


            
if __name__ == "__main__":
    # read config
    config = __import__('config')
    host = 		getattr(config, 'host', 'localhost')
    user = 		getattr(config, 'user', 'root')
    password = 	getattr(config, 'password', 'root')
    database = 	getattr(config, 'database', '')
    
    # Create DB connection
    connection = MySQLdb.connect (host = host,
                            user = user,
                            passwd = password,
                            db = database,
    						use_unicode = True,
    						charset = "utf8")
    
    app = QtGui.QApplication(sys.argv)
    mainForm = MainForm()
    init_exp()
    update_cam_list(0)
    videoStorage = DbFrameStorage(connection)
    mainForm.ui.timeSlider.setEnabled(False)
    mainForm.show()
    sys.exit(app.exec_())

