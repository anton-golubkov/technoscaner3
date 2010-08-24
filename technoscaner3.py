#!/usr/bin/python
# -*- coding: utf-8 -*-


import math
import MySQLdb
import cv
import sys
from PyQt4 import QtGui, QtCore
from PIL import Image
import StringIO
from progressbar import ProgressBar, Percentage, Bar




from mainform import Ui_Form
from analyzer import Analyzer

### Global variables ###

# Application main form
mainForm = None

# Database connection
connection = None

# Video-frames storage
videoStorage = None

# Image analyzer
analyzer = None

# Timer interval, ms
timerInterval = 10

# Recognized results list [(time, value, frame_id), ...]
results = []

class DbFrameStorage():
    """ Interface for acessing video from database """
    """ Video stored in table 'video' with columns (id, frame, time, experiment_id, sensor_id)"""
    def __init__(self, connection):
        self._connection = connection
        self._id_cursor = self._connection.cursor()
        self._frame_cursor = self._connection.cursor()
        self._current_frame = 0
        self._id = []
        self._time = []
        
    def open(self, expId, camId):
        """ Loads all frame id's from database with specified experiment_id and sensor_id """
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
    """ Loads template image into global variable templateContour for matching objects in video """
    global mainForm
    global analyzer
    fileName = QtGui.QFileDialog.getOpenFileName(mainForm, 
                                                 "Select template"
                                                 ".",
                                                 "Images (*.png *.xpm *.jpg *.bmp)")
    if len(fileName) > 0:
        templateContour = cv.LoadImage( unicode(fileName).encode("utf-8") , cv.CV_LOAD_IMAGE_GRAYSCALE)
        analyzer = Analyzer(templateContour)
        templatePixmap = QtGui.QPixmap()
        templatePixmap.load(fileName)
        mainForm.ui.templateImage.setPixmap(templatePixmap)



def init_exp():
    """ Load list of all experiments from database"""
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
        mainForm.ui.timeSlider.setValue(1)
        mainForm.ui.timeSlider.emit(QtCore.SIGNAL("valueChanged(int)"), 1)
    else:
        mainForm.ui.timeSlider.setMaximum(0)
        mainForm.ui.timeSlider.setEnabled(False)
        


def change_frame(frameNum):
    global mainForm
    global videoStorage
    global matchPoint
    global analyzer
    global results
    
    frame = videoStorage.getFrame(frameNum)
    pixmap = frame[0]
    ipl_image = frame[1]
   
    if analyzer != None:
        matchPoint = analyzer.findObject(ipl_image)
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

def save_results_from_gui():
    global results
    global connection
    global videoStorage
    save_results(results, connection, videoStorage.getExpId(), videoStorage.getCamId())
    

def save_results(results, connection, expId, camId):
    cursor = connection.cursor()
    cursor.execute("""INSERT INTO results_directory 
        (type, description, experiment_id, analizator_id, sensor_id) 
        VALUES( %s, %s, %s, %s, %s);""", 
        ("h", "h ts3", expId, 0, camId) )
    
    cursor.execute("SELECT LAST_INSERT_ID()")
    resultId = cursor.fetchone()[0]
    
    for i, item in enumerate(results):
        cursor.execute("""INSERT INTO results 
            (time, value, frame_id, distance_from_origin, result_id) 
            VALUES (%s, %s, %s, %s, %s);""", 
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
            save_results_from_gui)



def startCli(argv):
    """ 
    Command line interface version of programm
    
    Run analyze in batch mode, using parameters from config.py:
    cli_sensor_list - list of sensors
    cli_experiment_list - list of experiments
    cli_template_image - template image
    """
    global videoStorage
    global connection
    



    
    config = __import__('config')
    cli_sensor_list = 		getattr(config, 'cli_sensor_list', [])
    cli_experiment_list =   getattr(config, 'cli_experiment_list', [])
    cli_template_image = 	getattr(config, 'cli_template_image', '')
    template = cv.LoadImage(cli_template_image, cv.CV_LOAD_IMAGE_GRAYSCALE)
    analyzer = Analyzer(template)
    for experiment in cli_experiment_list:
        print "Start analyze experiment %s ..." % experiment
        for sensor in cli_sensor_list:
            print "Sensor %s" % sensor
            pbar = ProgressBar(widgets=[Percentage(), Bar()], maxval=100).start()
            results = []
            videoStorage.open(experiment, sensor)
            frameCount = videoStorage.getFrameCount()
            for frameNum in xrange( frameCount ):
                pbar.update(frameNum * 100 / frameCount)
                image = videoStorage.getFrame(frameNum)
                matchPoint = analyzer.findObject(image[1])
                # Add y coordinate of point to results
                results.append(  (  videoStorage.getFrameTime(frameNum), 
                        image[0].height() - matchPoint[1], 
                        videoStorage.getFrameId(frameNum) )  )
            save_results(results, connection, experiment, sensor)
            print "End analyze sensor %s" % sensor
            pbar.finish()
        print "End analyze experiment %s" % experiment
        print "------------------------------"          
                
    
    
    
    
def startGui(argv):
    """
    GUI version of programm
    
    """
    global mainForm
    
    
    mainForm = MainForm()
    init_exp()
    update_cam_list(0)
    mainForm.ui.timeSlider.setEnabled(False)
    mainForm.show()
    sys.exit(app.exec_())
    
            
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
    videoStorage = DbFrameStorage(connection)
    app = QtGui.QApplication(sys.argv)
    
    startCli(sys.argv)


