import copy
import sys

from PyQt5 import QtCore, QtWidgets
from PyQt5.Qt import *

from calc import Tape, LAMBDA, START_STATE


class TableModel(QAbstractTableModel):
    HEIGHT = 12
    WEIGHT = 12

    def __init__(self, parent=None):
        super(TableModel, self).__init__(parent)

        self.commands = [[['', False] for j in range(self.WEIGHT)] for i in range(self.HEIGHT)]
        self.commands[0][0] = ['Символ', False]
        self.commands[0][1] = [LAMBDA, False]
        self.commands[1][0] = [START_STATE, False]

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.commands)

    def columnCount(self, parent=None, *args, **kwargs):
        return self.WEIGHT

    def headerData(self, section, orientation, role=None):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                columns = ["Позиция", ]
                columns.extend(["" for _ in range(self.WEIGHT - 1)])
                return columns[section]

    def data(self, index, role):
        if index.isValid():
            data, changed = self.commands[index.row()][index.column()]

            if role in [Qt.DisplayRole, Qt.EditRole]:
                return data

    def setData(self, index, value, role):
        if role == Qt.EditRole:
            self.commands[index.row()][index.column()] = [value, True]
            return True
        return False

    def flags(self, index):
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

        self.button_export = QPushButton('Экспорт', self)
        self.button_export.move(900, 450)
        self.button_export.clicked.connect(self.show_export_dialog)

        self.button_import = QPushButton('Импорт', self)
        self.button_import.move(1000, 450)
        self.button_import.clicked.connect(self.show_import_dialog)

        self.arrow = QLabel(self)
        self.arrow.move(500, 395)
        self.arrow.resize(600, 30)
        self.arrow.setText('Указатель')
        self.arrow.setFont(QFont('Consolas', 24))

        self.tape = QLabel(self)
        self.tape.move(500, 420)
        self.tape.resize(600, 30)
        self.tape.setText('Строка')
        self.tape.setFont(QFont('Consolas', 24))

    def show_message(self, message: str):
        dlg = QDialog(self)
        dlg.setWindowTitle("Ошибка")
        layout = QVBoxLayout()
        message_elem = QLabel(message)
        layout.addWidget(message_elem)
        dlg.setLayout(layout)
        dlg.exec()

    @pyqtSlot()
    def on_click(self):
        textboxValue = self.textbox.text()
        index = self.textbox_index.text()
        if not index:
            self.show_message("Не задано начальное положение")
            return
        index = int(self.textbox_index.text())
        try:
            self.tape_cls = Tape(textboxValue, self.model.commands, index)
            self.tape.setText(''.join(self.tape_cls.state.tape))
            self.arrow.setText(self.tape_cls.state.arrow)
        except Exception as e:
            self.show_message(str(e))


    @pyqtSlot()
    def next_position(self):
        if self.tape_cls:
            try:
                ans = self.tape_cls.next()
                self.tape.setText(''.join(self.tape_cls.state.tape))
                self.arrow.setText(ans.arrow)
            except NotImplementedError:
                self.show_message("Неправильно задана функция")
            except Exception as e:
                self.show_message(str(e))

    @pyqtSlot()
    def go_to_end(self):
        c = 0
        while c < 1000 and not self.tape_cls.state.end:
            self.next_position()
            loop = QEventLoop()
            QTimer.singleShot(200, loop.quit)
            loop.exec_()
            c += 1

    @pyqtSlot()
    def make_graph(self):
        self.tape_cls.draw_graph()

    def make_export(self, filename: str):
        try:
            with open(f"{filename}", "w") as f:
                for row in self.model.commands:
                    f.write(";".join((i[0] for i in row)) + "\n")
        except Exception as e:
            self.show_message(f"Ошибка при экспорте: {e}")

    def make_import(self, filename: str):
        commands = copy.deepcopy(self.model.commands)
        try:
            with open(f"{filename}") as f:
                for row_index in range(self.model.HEIGHT):
                    row = f.readline().split(';')
                    for elem_index in range(self.model.WEIGHT):
                        commands[row_index][elem_index][0] = row[elem_index].strip()
        except Exception as e:
            self.show_message(f"Ошибка при импорте: {e}")
        self.model.commands = commands

    @pyqtSlot()
    def show_export_dialog(self):
        fname = QtWidgets.QFileDialog.getSaveFileName(self)[0]
        if fname:
            file_name = fname
            self.make_export(file_name)

    @pyqtSlot()
    def show_import_dialog(self):
        fname = QtWidgets.QFileDialog.getOpenFileName(self)[0]
        if fname:
            file_name = fname
            self.make_import(file_name)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.resize(1120, 500)
    mw.setWindowTitle('Машина Тьюринга')
    mw.show()
    sys.exit(app.exec_())
