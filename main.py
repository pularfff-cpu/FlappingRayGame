try:
    from PySide6 import QtCore, QtGui, QtWidgets
    from shiboken6 import wrapInstance
except:
    from PySide2 import QtCore, QtGui,QtWidgets
    from shiboken2 import wrapInstance

import maya.OpenMayaUI as omui
import maya.cmds as cmds
import sys
import random
import os
import importlib

from . import game
importlib.reload(game)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
RESOURCE_DIR = os.path.join(ROOT_DIR, 'resource')
HIGH_SCORE_FILE = os.path.join(RESOURCE_DIR, 'highscore.txt')


class FlappingRayDialog(QtWidgets.QDialog):

    BASE_BUTTON_STYLE = '''
        QPushButton {
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
    '''

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle('FlappingRay')
        
        self.high_score = 0
        self.loadHighScore()

        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)

        self.stackedWidget = QtWidgets.QStackedWidget()
        self.mainLayout.addWidget(self.stackedWidget)

        self.gamePage = game.FlappingGame(RESOURCE_DIR, parent=self)
        self.menuPage = self.createMenuPage() 
        self.stackedWidget.addWidget(self.menuPage)
        self.stackedWidget.addWidget(self.gamePage)

        self.gamePage.backToMenu.connect(self.showMenu)
        self.gamePage.gameFinished.connect(self.onGameFinished)

        self.resize(self.gamePage.GAME_WIDTH, self.gamePage.GAME_HEIGHT)
        self.showMenu()

    def createMenuPage(self):
        page = QtWidgets.QWidget()
        
        background_image_path = os.path.join(RESOURCE_DIR, 'image', 'background.gif')
        if os.path.exists(background_image_path):
            self.movieLabel = QtWidgets.QLabel(page)
            self.movie = QtGui.QMovie(background_image_path)
            self.movieLabel.setMovie(self.movie)
            self.movie.setScaledSize(
                QtCore.QSize(self.gamePage.GAME_WIDTH, self.gamePage.GAME_HEIGHT)
            )
            self.movie.start()
            self.movieLabel.setGeometry(0, 0, self.gamePage.GAME_WIDTH, self.gamePage.GAME_HEIGHT)
        else:
            page.setStyleSheet('background-color: #59E8E8;')
            
        buttonLayout = QtWidgets.QVBoxLayout(page) 
        buttonLayout.setAlignment(QtCore.Qt.AlignCenter)
        buttonLayout.addStretch()

        self.highScoreLabel = QtWidgets.QLabel(f"High Score: {self.high_score}")
        self.highScoreLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.highScoreLabel.setStyleSheet("""
            QLabel {
                font-size: 30px;
                color: orange;
                background-color: rgba(0, 0, 0, 0.5);
                font-weight: bold;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        buttonLayout.addWidget(self.highScoreLabel)
        buttonLayout.addSpacing(15)

        logo_image_path = os.path.join(RESOURCE_DIR, 'image', 'ray.png')
        if os.path.exists(logo_image_path):
            logo_label = QtWidgets.QLabel()
            logo_pixmap = QtGui.QPixmap(logo_image_path)
            logo_label.setPixmap(logo_pixmap.scaled(
                200, 200, 
                QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation
            ))
            logo_label.setAlignment(QtCore.Qt.AlignCenter)
            buttonLayout.addWidget(logo_label)
            buttonLayout.addSpacing(20) 

        self.startButton = QtWidgets.QPushButton('Start')
        self.startButton.setStyleSheet(f"QPushButton {{ background-color: Green; }} {self.BASE_BUTTON_STYLE}")
        self.startButton.clicked.connect(self.startGame)

        icon_path = os.path.join(RESOURCE_DIR, 'image', 'ray.png')
        if os.path.exists(icon_path):
             self.startButton.setIcon(QtGui.QIcon(icon_path))
             self.startButton.setIconSize(QtCore.QSize(40, 40))

        self.cancelButton = QtWidgets.QPushButton('Cancel')
        self.cancelButton.setStyleSheet(f"QPushButton {{ background-color: red; }} {self.BASE_BUTTON_STYLE}")
        self.cancelButton.clicked.connect(self.close)

        buttonLayout.addWidget(self.startButton)
        buttonLayout.addWidget(self.cancelButton)
        buttonLayout.addStretch()

        return page

    def startGame(self):
        self.stackedWidget.setCurrentWidget(self.gamePage)
        self.gamePage.restartGame()

    def showMenu(self):
        if hasattr(self, 'highScoreLabel'):
            self.highScoreLabel.setText(f"High Score: {self.high_score}")
            
        self.stackedWidget.setCurrentWidget(self.menuPage)
        if hasattr(self, 'movie'):
            self.movie.start()

    def loadHighScore(self):
        try:
            if os.path.exists(HIGH_SCORE_FILE):
                with open(HIGH_SCORE_FILE, 'r') as f:
                    self.high_score = int(f.read().strip())
            else:
                self.high_score = 0
        except Exception as e:
            print(f"can't load High Score: {e}")
            self.high_score = 0

    def saveHighScore(self):
        try:
            with open(HIGH_SCORE_FILE, 'w') as f:
                f.write(str(self.high_score))
        except Exception as e:
            print(f"can't save High Score: {e}")

    def onGameFinished(self, final_score):
        print(f"Score: {final_score}, High Score : {self.high_score}")
        if final_score > self.high_score:
            self.high_score = final_score
            self.saveHighScore()
            print(f"High Score : {self.high_score}")

    def closeEvent(self, event):
        self.gamePage.timer.stop()
        if hasattr(self, 'movie'):
            self.movie.stop()
        event.accept()


def run():
    global ui
    try:
        ui.close()
        ui.deleteLater()
    except:
        pass

    SPHERE_NAME = "flapping_ray_locator"
    
    if not cmds.objExists(SPHERE_NAME):
        cmds.sphere(name=SPHERE_NAME, radius=2)
        

    ptr = wrapInstance(int(omui.MQtUtil.mainWindow()), QtWidgets.QWidget)
    ui = FlappingRayDialog(parent=ptr)
    ui.show()