import sys
import time

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.Qt import *

from calc import Tape


class TableModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super(TableModel, self).__init__(parent)

        self.tasks = [[['', False] for j in range(10)] for i in range(12)]  # +++
        self.tasks[0][0] = ['Символ', False]

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.tasks)

    def columnCount(self, parent=None, *args, **kwargs):
        return 10

    def headerData(self, section, orientation, role=None):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return ["Позиция", "", "", "", "", "", "", "", "", ""][section]

    def data(self, index, role):
        if index.isValid():
            data, changed = self.tasks[index.row()][index.column()]

            if role in [Qt.DisplayRole, Qt.EditRole]:
                return data

    def setData(self, index, value, role):  # !!!
        if role == Qt.EditRole:
            self.tasks[index.row()][index.column()] = [value, True]
            return True
        return False

    def flags(self, index):  # !!!
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable


class MainWindow(QMainWindow):
    tape_cls = None

    def __init__(self):
        super().__init__()

        self.model = TableModel()
        self.table = QTableView()
        # self.table.verticalHeader().hide()
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setModel(self.model)

        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        grid = QGridLayout(centralWidget)
        grid.addWidget(self.table, 0, 0)

        self.label_index = QLabel(self)
        self.label_index.move(20, 410)
        self.label_index.resize(280, 30)
        self.label_index.setText('Стартовая позиция')

        self.textbox_index = QLineEdit(self)
        self.textbox_index.move(200, 410)
        self.textbox_index.resize(280, 30)

        self.label_tape = QLabel(self)
        self.label_tape.move(20, 450)
        self.label_tape.resize(280, 30)
        self.label_tape.setText('Запись')

        self.textbox = QLineEdit(self)
        self.textbox.move(200, 450)
        self.textbox.resize(280, 30)

        self.button_install = QPushButton('Установить', self)
        self.button_install.move(500, 450)
        self.button_install.clicked.connect(self.on_click)

        self.button_next = QPushButton('Сделать шаг', self)
        self.button_next.move(600, 450)
        self.button_next.clicked.connect(self.next_position)

        self.button_auto = QPushButton('Автоматически', self)
        self.button_auto.move(700, 450)
        self.button_auto.clicked.connect(self.go_to_end)

        self.button_auto = QPushButton('Диаграмма', self)
        self.button_auto.move(800, 450)
        self.button_auto.clicked.connect(self.make_graph)

        self.arrow = QLabel(self)
        self.arrow.move(500, 395)
        self.arrow.resize(280, 30)
        self.arrow.setText('Указатель')
        self.arrow.setFont(QFont('Consolas', 24))

        self.tape = QLabel(self)
        self.tape.move(500, 420)
        self.tape.resize(280, 30)
        self.tape.setText('Строка')
        self.tape.setFont(QFont('Consolas', 24))

    @pyqtSlot()
    def on_click(self):
        textboxValue = self.textbox.text()
        index = int(self.textbox_index.text())
        self.tape_cls = Tape(textboxValue, self.model.tasks, index)
        self.tape.setText(''.join(self.tape_cls.state.tape))
        self.arrow.setText(self.tape_cls.state.arrow)

    @pyqtSlot()
    def next_position(self):
        if self.tape_cls:
            ans = self.tape_cls.next()
            self.tape.setText(''.join(self.tape_cls.state.tape))
            self.arrow.setText(ans.arrow)

    @pyqtSlot()
    def go_to_end(self):
        c = 0
        while c < 1000 and not self.tape_cls.state.end:
            self.next_position()
            loop = QEventLoop()
            QTimer.singleShot(1000, loop.quit)
            loop.exec_()
            c += 1

    @pyqtSlot()
    def make_graph(self):
        self.tape_cls.draw_graph()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.resize(930, 500)
    mw.show()
    sys.exit(app.exec_())
