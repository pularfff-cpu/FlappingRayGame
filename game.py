from PySide6 import QtCore, QtGui, QtWidgets
import random

ROOT_RESOURCE_DIR = 'C:/Users/User/Documents/maya/2025/scripts/FlappingRay/resource'

class FlappingGame(QtWidgets.QWidget):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setWindowTitle("Flapping Ray")
		self.resize(400, 600)
		self.setStyleSheet("background-color: skyblue;")

	#ตัวแปรเกมหลัก
		self.bird_y = 250
		self.bird_speed = 0
		self.gravity = 0.5
		self.pipe_x = 400
		self.pipe_gap = 150
		self.pipe_height = random.randint(100, 400)
		self.score = 0
		self.passed_pipe = False
		self.is_game_over = False
		self.bird_pixmap = QtGui.QPixmap(f"{ROOT_RESOURCE_DIR}/image/ray.png")
		self.pipe_top_pixmap = QtGui.QPixmap(f"{ROOT_RESOURCE_DIR}/image/pipe_up.png")
		self.pipe_bottom_pixmap = QtGui.QPixmap(f"{ROOT_RESOURCE_DIR}/image/pipe_down.png")


	# ==== ตั้ง Timer สำหรับอัปเดตเกม ====
		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.updateGame)
		self.timer.start(30)

	# ==== สร้าง Layout ====
		self.mainLayout = QtWidgets.QVBoxLayout(self)
		self.mainLayout.setAlignment(QtCore.Qt.AlignCenter)

		self.buttonLayout = QtWidgets.QVBoxLayout()
		self.buttonLayout.setAlignment(QtCore.Qt.AlignCenter)

	# ==== ปุ่ม Restart ====
		self.restartButton = QtWidgets.QPushButton("Restart", self)
		self.restartButton.setStyleSheet('''
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
		self.restartButton.hide()
		self.restartButton.clicked.connect(self.restartGame)

		self.buttonLayout.addWidget(self.restartButton)
		self.mainLayout.addLayout(self.buttonLayout)
	
	# คลิกเพื่อบินขึ้น
	def mousePressEvent(self, event):
		if not self.is_game_over:
			self.bird_speed = -7
	
	# วาดภาพทั้งหมด
	def paintEvent(self, event):
		painter = QtGui.QPainter(self)
		
		# วาดนก
		if not self.bird_pixmap.isNull():
			painter.drawPixmap(100, int(self.bird_y), 40, 40, self.bird_pixmap)
		else:
			painter.setBrush(QtGui.QBrush(QtGui.QColor("yellow")))
			painter.drawEllipse(100, self.bird_y, 30, 30)

		# วาดท่อ
		if not self.pipe_top_pixmap.isNull() and not self.pipe_bottom_pixmap.isNull():
			painter.drawPixmap(self.pipe_x, 0, 60, self.pipe_height, self.pipe_top_pixmap)
			painter.drawPixmap(
				self.pipe_x,
				self.pipe_height + self.pipe_gap,
				60,
				600 - self.pipe_height - self.pipe_gap,
				self.pipe_bottom_pixmap
			)
		else:
		# fallback ถ้าโหลดรูปไม่ได้
			painter.setBrush(QtGui.QBrush(QtGui.QColor("green")))
			painter.drawRect(self.pipe_x, 0, 60, self.pipe_height)
			painter.drawRect(
				self.pipe_x,
				self.pipe_height + self.pipe_gap,
				60,
				600 - self.pipe_height - self.pipe_gap
			)

		# วาดคะแนน
		painter.setPen(QtGui.QPen(QtCore.Qt.black))
		painter.setFont(QtGui.QFont("Arial", 20, QtGui.QFont.Bold))
		painter.drawText(10, 50, f"Score: {self.score}")

		# วาดข้อความ Game Over
		if self.is_game_over:
			painter.setPen(QtGui.QPen(QtCore.Qt.red))
			painter.setFont(QtGui.QFont("Arial", 28, QtGui.QFont.Bold))
			painter.drawText(100, 250, "GAME OVER")

	# อัปเดตสถานะเกมทุกเฟรม
	def updateGame(self):
		if self.is_game_over:
			return

		# การเคลื่อนไหวของนก
		self.bird_y += self.bird_speed
		self.bird_speed += self.gravity

		# การเคลื่อนไหวของท่อ
		self.pipe_x -= 4
		if self.pipe_x < -60:
			self.pipe_x = 400
			self.pipe_height = random.randint(100, 400)
			self.passed_pipe = False

		# ตรวจจับว่าผ่านท่อสำเร็จหรือยัง (เพิ่มคะแนน)
		if self.pipe_x + 60 < 100 and not self.passed_pipe:
			self.score += 1
			self.passed_pipe = True

		# ตรวจจับการชน
		self.checkCollision()

		self.update()

	# ตรวจจับชนท่อหรือพื้น / เพดาน
	def checkCollision(self):
		bird_rect = QtCore.QRect(100, int(self.bird_y), 30, 30)
		top_pipe_rect = QtCore.QRect(self.pipe_x, 0, 60, self.pipe_height)
		bottom_pipe_rect = QtCore.QRect(
			self.pipe_x,
			self.pipe_height + self.pipe_gap,
			60,
			600 - self.pipe_height - self.pipe_gap
		)

		# ชนท่อบน / ล่าง
		if bird_rect.intersects(top_pipe_rect) or bird_rect.intersects(bottom_pipe_rect):
			self.gameOver()
			return

		# ชนขอบบน/ล่างจอ
		if self.bird_y < 0 or self.bird_y + 30 > 600:
			self.gameOver()
	# Game Over
	def gameOver(self):
		self.is_game_over = True
		self.timer.stop()
		self.restartButton.show()
	# เริ่มเกมใหม่
	def restartGame(self):
		self.bird_y = 250
		self.bird_speed = 0
		self.pipe_x = 400
		self.pipe_height = random.randint(100, 400)
		self.score = 0
		self.passed_pipe = False
		self.is_game_over = False
		self.restartButton.hide()
		self.timer.start(30)
		self.update()