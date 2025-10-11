from PySide6 import QtCore, QtGui, QtWidgets
import random

class FlappingGame(QtWidgets.QWidget):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setWindowTitle("Flapping Bird")
		self.resize(400, 600)
		self.setStyleSheet("background-color: skyblue;")

		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.updateGame)
		self.timer.start(30)

		self.bird_y = 250
		self.bird_speed = 0
		self.gravity = 0.5

		self.pipe_x = 400
		self.pipe_gap = 150
		self.pipe_height = random.randint(100, 400)

		# คลิกเพื่อบิน
		self.setMouseTracking(True)

	def mousePressEvent(self, event):
		self.bird_speed = -7  # กระโดดขึ้นเมื่อคลิก

	def paintEvent(self, event):
		painter = QtGui.QPainter(self)

		# วาดนก
		painter.setBrush(QtGui.QBrush(QtGui.QColor("yellow")))
		painter.drawEllipse(100, self.bird_y, 30, 30)

		# วาดท่อ
		painter.setBrush(QtGui.QBrush(QtGui.QColor("green")))
		painter.drawRect(self.pipe_x, 0, 60, self.pipe_height)
		painter.drawRect(self.pipe_x, self.pipe_height + self.pipe_gap,
						 60, 600 - self.pipe_height - self.pipe_gap)

	def updateGame(self):
		# แรงโน้มถ่วง
		self.bird_y += self.bird_speed
		self.bird_speed += self.gravity

		# ท่อเลื่อน
		self.pipe_x -= 4
		if self.pipe_x < -60:
			self.pipe_x = 400
			self.pipe_height = random.randint(100, 400)

		self.update()
