# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainform.ui'
#
# Created: Wed Aug 18 22:20:46 2010
#      by: PyQt4 UI code generator 4.7.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(790, 535)
        self.verticalLayout_2 = QtGui.QVBoxLayout(Form)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.image = QtGui.QLabel(Form)
        self.image.setMinimumSize(QtCore.QSize(640, 480))
        self.image.setObjectName("image")
        self.horizontalLayout.addWidget(self.image)
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.experimentList = QtGui.QComboBox(Form)
        self.experimentList.setObjectName("experimentList")
        self.verticalLayout_3.addWidget(self.experimentList)
        self.cameraList = QtGui.QComboBox(Form)
        self.cameraList.setObjectName("cameraList")
        self.verticalLayout_3.addWidget(self.cameraList)
        self.openButton = QtGui.QPushButton(Form)
        self.openButton.setObjectName("openButton")
        self.verticalLayout_3.addWidget(self.openButton)
        self.selectTemplateButton = QtGui.QPushButton(Form)
        self.selectTemplateButton.setObjectName("selectTemplateButton")
        self.verticalLayout_3.addWidget(self.selectTemplateButton)
        self.saveResultsButton = QtGui.QPushButton(Form)
        self.saveResultsButton.setObjectName("saveResultsButton")
        self.verticalLayout_3.addWidget(self.saveResultsButton)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem)
        self.templateImage = QtGui.QLabel(Form)
        self.templateImage.setObjectName("templateImage")
        self.verticalLayout_3.addWidget(self.templateImage)
        self.graphic = QtGui.QLabel(Form)
        self.graphic.setMinimumSize(QtCore.QSize(100, 100))
        self.graphic.setObjectName("graphic")
        self.verticalLayout_3.addWidget(self.graphic)
        self.horizontalLayout.addLayout(self.verticalLayout_3)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.timeSlider = QtGui.QSlider(Form)
        self.timeSlider.setOrientation(QtCore.Qt.Horizontal)
        self.timeSlider.setObjectName("timeSlider")
        self.horizontalLayout_2.addWidget(self.timeSlider)
        self.playButton = QtGui.QPushButton(Form)
        self.playButton.setObjectName("playButton")
        self.horizontalLayout_2.addWidget(self.playButton)
        self.pauseButton = QtGui.QPushButton(Form)
        self.pauseButton.setObjectName("pauseButton")
        self.horizontalLayout_2.addWidget(self.pauseButton)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Technoscaner 3 Alpha-1", None, QtGui.QApplication.UnicodeUTF8))
        self.image.setText(QtGui.QApplication.translate("Form", "Image", None, QtGui.QApplication.UnicodeUTF8))
        self.openButton.setText(QtGui.QApplication.translate("Form", "Open", None, QtGui.QApplication.UnicodeUTF8))
        self.selectTemplateButton.setText(QtGui.QApplication.translate("Form", "Select template", None, QtGui.QApplication.UnicodeUTF8))
        self.saveResultsButton.setText(QtGui.QApplication.translate("Form", "Save", None, QtGui.QApplication.UnicodeUTF8))
        self.templateImage.setText(QtGui.QApplication.translate("Form", "Template", None, QtGui.QApplication.UnicodeUTF8))
        self.graphic.setText(QtGui.QApplication.translate("Form", "Graphic", None, QtGui.QApplication.UnicodeUTF8))
        self.playButton.setText(QtGui.QApplication.translate("Form", "Play", None, QtGui.QApplication.UnicodeUTF8))
        self.pauseButton.setText(QtGui.QApplication.translate("Form", "Pause", None, QtGui.QApplication.UnicodeUTF8))

