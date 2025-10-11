try:
	from PySide6 import QtCore, QtGui, QtWidgets
	from shiboken6 import wrapInstance
except:
	from PySide2 import QtCore, QtGui,QtWidgets
	from shiboken2 import wrapInstance

import maya.OpenMayaUI as omui
import sys
import random

import importlib
from . import util
importlib.reload(util)
from . import game
importlib.reload(game)


ROOT_RESOURCE_DIR = 'C:/Users/User/Documents/maya/2025/scripts/FlappingRay/resource'

class FlappingRayDialog(QtWidgets.QDialog):
	def __init__(self, parent=None):
		super().__init__(parent)

		self.setWindowTitle('FlappingRay')
		self.resize(400, 600)
		self.setStyleSheet('background-color: #59EBE8;')

		self.mainLayout = QtWidgets.QVBoxLayout(self)
		self.mainLayout.setAlignment(QtCore.Qt.AlignCenter)

		self.buttonLayout = QtWidgets.QVBoxLayout()
		self.buttonLayout.setAlignment(QtCore.Qt.AlignCenter)

		self.startButton = QtWidgets.QPushButton('Start')
		self.startButton.setStyleSheet('''
			QPushButton {
				background-color: green;
				color: white;
				border-radius: 10px;
				font-size: 50px;
				padding: 8px;
				font-weight: bold;
			}
			QPushButton:hover {
				background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
				stop:0 red, stop:1 blue);
			}
			QPushButton:pressed {
				background-color: navy;
			}
		''')
		self.startButton.clicked.connect(self.startGame)

		self.cancelButton = QtWidgets.QPushButton('Cancel')
		self.cancelButton.setStyleSheet('''
			QPushButton {
				background-color: red;
				color: white;
				border-radius: 10px;
				font-size: 50px;
				padding: 8px;
				font-weight: bold;
			}
			QPushButton:hover {
				background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
				stop:0 red, stop:1 blue);
			}
			QPushButton:pressed {
				background-color: navy;
			}
		''')
		self.cancelButton.clicked.connect(self.close)

		self.buttonLayout.addWidget(self.startButton)
		self.buttonLayout.addWidget(self.cancelButton)

		self.mainLayout.addLayout(self.buttonLayout)
	def startGame(self):
		self.gameWindow = game.FlappingGame(parent=self)
		self.gameWindow.show()

def run():
	global ui
	try:
		ui.close()
	except:
		pass

	ptr = wrapInstance(int(omui.MQtUtil.mainWindow()),QtWidgets.QWidget)
	ui = FlappingRayDialog(parent=ptr)
	ui.show()