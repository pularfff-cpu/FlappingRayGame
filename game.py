from PySide6 import QtCore, QtGui, QtWidgets
import random
import os
import maya.cmds as cmds

GAME_BUTTON_STYLE = '''
    QPushButton {
        color: white;
        border-radius: 10px;
        font-size: 30px;
        padding: 8px;
        font-weight: bold;
        min-width: 180px;
    }
    QPushButton:hover {
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 red, stop:1 blue);
    }
    QPushButton:pressed {
        background-color: navy;
    }
'''

class FlappingGame(QtWidgets.QWidget):

    backToMenu = QtCore.Signal()
    gameFinished = QtCore.Signal(int)

    # --- Game Constants ---
    GAME_WIDTH = 400
    GAME_HEIGHT = 600
    GRAVITY = 0.5
    FLAP_STRENGTH = -7
    PIPE_SPEED = 4
    PIPE_GAP = 150

    RAY_X_POS = 100
    RAY_WIDTH = 40
    RAY_HEIGHT = 40

    PIPE_WIDTH = 60
    PIPE_MIN_HEIGHT = 100
    PIPE_MAX_HEIGHT = 400

    def __init__(self, resource_dir, parent=None):
        super().__init__(parent)

        self.resize(self.GAME_WIDTH, self.GAME_HEIGHT)
        self.resource_dir = resource_dir

        self.gameMovie = None
        game_background_path = os.path.join(self.resource_dir, 'image', 'background.gif')

        if os.path.exists(game_background_path):
            self.gameMovie = QtGui.QMovie(game_background_path)
            self.gameMovie.setScaledSize(
                QtCore.QSize(self.GAME_WIDTH, self.GAME_HEIGHT)
            )
            self.gameMovie.updated.connect(self.update)

        self.game_over_pixmap = None
        game_over_icon_path = os.path.join(self.resource_dir, 'image', 'game_over_icon.png')
        if os.path.exists(game_over_icon_path):
            self.game_over_pixmap = QtGui.QPixmap(game_over_icon_path)
           
            self.game_over_pixmap = self.game_over_pixmap.scaled(
                 200, 100, # ขนาดที่ต้องการ
                 QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation
             )

        self.ray_y = self.GAME_HEIGHT // 2
        self.ray_speed = 0
        self.score = 0
        self.passed_pipe = False
        self.is_game_over = False

        self.pipe_x = self.GAME_WIDTH + 100
        self.pipe_height = random.randint(self.PIPE_MIN_HEIGHT, self.PIPE_MAX_HEIGHT)

        self.ray_pixmap = QtGui.QPixmap(os.path.join(self.resource_dir, 'image', 'ray.png'))
        self.pipe_top_pixmap = QtGui.QPixmap(os.path.join(self.resource_dir, 'image', 'pipe_up.png'))
        self.pipe_bottom_pixmap = QtGui.QPixmap(os.path.join(self.resource_dir, 'image', 'pipe_down.png'))

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updateGame)

        # Layout สำหรับปุ่ม
        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.mainLayout.setAlignment(QtCore.Qt.AlignCenter)

        self.buttonLayout = QtWidgets.QVBoxLayout()
        self.buttonLayout.setAlignment(QtCore.Qt.AlignCenter)
        self.buttonLayout.setSpacing(10)

        self.restartButton = QtWidgets.QPushButton("Restart", self)
        self.restartButton.setStyleSheet(f"QPushButton {{ background-color: red; }} {GAME_BUTTON_STYLE}")
        self.restartButton.hide()
        self.restartButton.clicked.connect(self.restartGame)

        self.menuButton = QtWidgets.QPushButton("Main Menu", self)
        self.menuButton.setStyleSheet(f"QPushButton {{ background-color: skyblue; }} {GAME_BUTTON_STYLE}")
        self.menuButton.hide()
        self.menuButton.clicked.connect(self.goBackToMenu)

        self.buttonLayout.addWidget(self.restartButton)
        self.buttonLayout.addWidget(self.menuButton)
        self.mainLayout.addLayout(self.buttonLayout)


    def mousePressEvent(self, event):
        if not self.is_game_over:
            self.ray_speed = self.FLAP_STRENGTH

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)

        if self.gameMovie and self.gameMovie.isValid():
            current_frame_pixmap = self.gameMovie.currentPixmap()
            painter.drawPixmap(0, 0, current_frame_pixmap)
        else:
            painter.setBrush(QtGui.QBrush(QtGui.QColor("skyblue")))
            painter.drawRect(self.rect()) 

        # วาดนก
        if not self.ray_pixmap.isNull():
            painter.drawPixmap(
                self.RAY_X_POS, int(self.ray_y), 
                self.RAY_WIDTH, self.RAY_HEIGHT, 
                self.ray_pixmap
            )
        else:
            painter.setBrush(QtGui.QBrush(QtGui.QColor("yellow")))
            painter.drawEllipse(
                self.RAY_X_POS, int(self.ray_y), 
                self.RAY_WIDTH, self.RAY_HEIGHT
            )

        # วาดท่อ
        pipe_bottom_y = self.pipe_height + self.PIPE_GAP
        pipe_bottom_height = self.GAME_HEIGHT - pipe_bottom_y

        if not self.pipe_top_pixmap.isNull() and not self.pipe_bottom_pixmap.isNull():
            painter.drawPixmap(
                self.pipe_x, 0, 
                self.PIPE_WIDTH, self.pipe_height, 
                self.pipe_top_pixmap
            )
            painter.drawPixmap(
                self.pipe_x, pipe_bottom_y,
                self.PIPE_WIDTH, pipe_bottom_height,
                self.pipe_bottom_pixmap
            )
        else:
            painter.setBrush(QtGui.QBrush(QtGui.QColor("green")))
            painter.drawRect(self.pipe_x, 0, self.PIPE_WIDTH, self.pipe_height)
            painter.drawRect(self.pipe_x, pipe_bottom_y, self.PIPE_WIDTH, pipe_bottom_height)

        # วาดคะแนน
        painter.setPen(QtGui.QPen(QtCore.Qt.blue))
        painter.setFont(QtGui.QFont("Arial", 20, QtGui.QFont.Bold))
        painter.drawText(10, 50, f"Score: {self.score}")

        if self.is_game_over and self.game_over_pixmap and not self.game_over_pixmap.isNull():
            icon_width = self.game_over_pixmap.width()
            icon_height = self.game_over_pixmap.height()

            x_pos = (self.GAME_WIDTH - icon_width) // 2
            y_pos = (self.GAME_HEIGHT - icon_height) // 2 - 150 
            painter.drawPixmap(x_pos, y_pos, self.game_over_pixmap)

        self.MAYA_SPHERE_NAME = "flapping_ray_locator"
        self.MAYA_SCALE_FACTOR = 10.0
        
        self.MAYA_SCALE_HEIGHT = self.GAME_HEIGHT / self.MAYA_SCALE_FACTOR
        self.MAYA_X_POS = self.RAY_X_POS / self.MAYA_SCALE_FACTOR

        self.maya_sphere_exists = cmds.objExists(self.MAYA_SPHERE_NAME) 
        if self.maya_sphere_exists:
            try:
                cmds.setAttr(f"{self.MAYA_SPHERE_NAME}.translateX", self.MAYA_X_POS) # <---
            except Exception as e:
                print(f"ไม่สามารถตั้งค่า X: {e}")
                self.maya_sphere_exists = False

    def updateGame(self):
        if self.is_game_over:
            return

        self.ray_y += self.ray_speed
        self.ray_speed += self.GRAVITY

        if self.maya_sphere_exists:
            try:
                maya_y = self.MAYA_SCALE_HEIGHT - (self.ray_y / self.MAYA_SCALE_FACTOR)
                cmds.setAttr(f"{self.MAYA_SPHERE_NAME}.translateY", maya_y)
            
            except Exception as e:
                print(f"Error updating Maya sphere: {e}")
                self.maya_sphere_exists = False

        self.pipe_x -= self.PIPE_SPEED
        if self.pipe_x < -self.PIPE_WIDTH:
            self.pipe_x = self.GAME_WIDTH
            self.pipe_height = random.randint(self.PIPE_MIN_HEIGHT, self.PIPE_MAX_HEIGHT)
            self.passed_pipe = False

        if (self.pipe_x + self.PIPE_WIDTH) < self.RAY_X_POS and not self.passed_pipe:
            self.score += 1
            self.passed_pipe = True

        self.checkCollision()
        self.update()


    def checkCollision(self):
        ray_rect = QtCore.QRect(
            self.RAY_X_POS, int(self.ray_y), 
            self.RAY_WIDTH, self.RAY_HEIGHT
        )

        top_pipe_rect = QtCore.QRect(
            self.pipe_x, 0, 
            self.PIPE_WIDTH, self.pipe_height
        )

        bottom_pipe_y = self.pipe_height + self.PIPE_GAP
        bottom_pipe_height = self.GAME_HEIGHT - bottom_pipe_y
        bottom_pipe_rect = QtCore.QRect(
            self.pipe_x, bottom_pipe_y,
            self.PIPE_WIDTH, bottom_pipe_height
        )

        if ray_rect.intersects(top_pipe_rect) or ray_rect.intersects(bottom_pipe_rect):
            self.gameOver()
            return

        if self.ray_y < 0 or (self.ray_y + self.RAY_HEIGHT) > self.GAME_HEIGHT:
            self.gameOver()

    def gameOver(self):
        if self.is_game_over:
            return

        self.is_game_over = True
        self.timer.stop()
        if self.gameMovie:
            self.gameMovie.stop()

        self.gameFinished.emit(self.score)

        self.restartButton.show()
        self.menuButton.show()

    def goBackToMenu(self):
        self.is_game_over = True
        self.timer.stop()
        if self.gameMovie:
            self.gameMovie.stop()
        self.restartButton.hide()
        self.menuButton.hide()
        self.backToMenu.emit()

    def restartGame(self):
        self.ray_y = self.GAME_HEIGHT // 2
        self.ray_speed = 0
        self.pipe_x = self.GAME_WIDTH + 100
        self.pipe_height = random.randint(self.PIPE_MIN_HEIGHT, self.PIPE_MAX_HEIGHT)
        self.score = 0
        self.passed_pipe = False
        self.is_game_over = False

        self.restartButton.hide()
        self.menuButton.hide()

        if self.gameMovie:
            self.gameMovie.start()

        self.timer.start(30)
        self.update()