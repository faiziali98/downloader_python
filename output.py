# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dui.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from downloader import *
import curses
import shutil


class Ui_Dialog(object):
    def __init__(self):
        super(Ui_Dialog, self).__init__()
        Dialog = QtWidgets.QDialog()

        Dialog.setObjectName("Downloader")
        Dialog.resize(604, 249)
        app_icon = QtGui.QIcon()
        app_icon.addFile('down.png')
        Dialog.setWindowIcon(app_icon)

        self.setup(Dialog)
        self.retranslateUi(Dialog)
        Dialog.show()

    def setup(self, Dialog):

        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(490, 30, 81, 101))
        self.buttonBox.setOrientation(QtCore.Qt.Vertical)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.progressBar = QtWidgets.QProgressBar(Dialog)
        self.progressBar.setGeometry(QtCore.QRect(120, 160, 351, 24))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.textEdit = QtWidgets.QTextEdit(Dialog)
        self.textEdit.setGeometry(QtCore.QRect(200, 30, 241, 21))
        self.textEdit.setObjectName("textEdit")
        self.textEdit_2 = QtWidgets.QTextEdit(Dialog)
        self.textEdit_2.setGeometry(QtCore.QRect(200, 80, 241, 21))
        self.textEdit_2.setObjectName("textEdit_2")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(40, 30, 151, 22))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(40, 80, 151, 22))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(40, 120, 180, 22))
        self.label_3.setObjectName("label_2")

        self.buttonBox.accepted.connect(lambda: self.download(Dialog))
        self.buttonBox.rejected.connect(lambda: self.clearing(Dialog))

    def clearing(self, Dialog):
        curses.echo()
        curses.nocbreak()
        curses.endwin()
        Dialog.accept()

    def download(self, Dialog):
        file = self.textEdit.toPlainText()
        url = self.textEdit_2.toPlainText()

        if file == '' or url == '':
            self.label_3.setText("Error: Enter Url and Filename")
        else:
            try:
                PBAR = self.progressBar
                downloadHelp(
                    self.textEdit.toPlainText(), 
                    self.textEdit_2.toPlainText(),
                    self.progressBar
                )
                self.clearing(Dialog)
            except:
                self.label_3.setText("Dialog", "Error: Invalid url or filename")
                return

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Downloader"))
        self.label.setText(_translate("Dialog", "Enter File Name"))
        self.label_2.setText(_translate("Dialog", "Enter Url"))
        self.label_3.setText(_translate("Dialog", ""))


if __name__ == "__main__":
    import sys
    curses.noecho()
    curses.cbreak()

    app = QtWidgets.QApplication(sys.argv)
    ui = Ui_Dialog()

    sys.exit(app.exec_())
