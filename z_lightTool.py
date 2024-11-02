import sys
from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtGui import QPainter, QBrush, QPen
from PyQt5.QtCore import Qt, pyqtSignal

class CircleLabel(QLabel):
    # 定义一个信号，传递当前状态
    stateChanged = pyqtSignal(int)

    def __init__(self, fixsize = 40, parent=None):
        super(CircleLabel, self).__init__(parent)
        self.setFixedSize(fixsize, fixsize)  # 设置标签的固定大小
        self._state = 0  # 初始状态为1（绿色）

    def setState(self, state):
        """
        设置当前状态。
        :param state: 整数，1表示绿色，0表示红色
        """
        state = 1 if state > 0 else 0
        
        if self._state != state:
            self._state = state
            self.stateChanged.emit(self._state)  # 发出信号
            self.update()  # 触发重绘

    def toggleState(self):
        """
        切换状态。
        """
        new_state = 0 if self._state == 1 else 1
        self.setState(new_state)

    def getState(self):
        """
        获取当前状态。
        :return: 当前状态（0或1）
        """
        return self._state

    def paintEvent(self, event):
        # 创建一个QPainter对象
        painter = QPainter(self)
        
        # 根据当前状态设置画刷颜色
        if self._state == 1:
            brush = QBrush(Qt.green, Qt.SolidPattern)
        else:
            brush = QBrush(Qt.red, Qt.SolidPattern)
        painter.setBrush(brush)

        # 设置无边框线
        pen = QPen(Qt.NoPen)
        painter.setPen(pen)

        # 获取标签的矩形区域
        rect = self.rect()

        # 在矩形区域内绘制一个圆形
        painter.drawEllipse(rect)
        
        painter.end()

class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.circle_label = CircleLabel()
        self.button = QPushButton("切换状态")
        self.button.clicked.connect(self.circle_label.toggleState)

        # 连接信号到槽函数
        self.circle_label.stateChanged.connect(self.on_state_changed)

        layout = QVBoxLayout()
        layout.addWidget(self.circle_label)
        layout.addWidget(self.button)
        self.setLayout(layout)
        self.setWindowTitle("CircleLabel 状态切换示例")

    def on_state_changed(self, state):
        if state == 1:
            print("状态已更改为：绿色")
        elif state == 0:
            print("状态已更改为：红色")

if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
