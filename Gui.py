__autor__ = 'Gaetan'

import sys
import time

from PyQt5.QtWidgets import (QApplication, QWidget, QLineEdit, QLabel,
                             QVBoxLayout, QHBoxLayout, QPushButton,
                             QMessageBox, QComboBox)
from PyQt5.QtCore import QObject, QThread, pyqtSlot, pyqtSignal
from Reseau import Reseau
from Planning import Planning
from ComUsb import ComUsb
from api_client import Client
from smartcard.CardMonitoring import CardMonitor
import config

class GuiLogger(QWidget):
    def __init__(self):
        super().__init__()
        self.reseau = Reseau()
        self.planning = Planning()
        self.createLogger()

    def createLogger(self):
        self.setGeometry(300, 300, 300, 220)
        self.setWindowTitle('Connexion')

        # create layout vertical contenant les layouts horizontaux
        vbox = QVBoxLayout(self)

        boxLoggin = QHBoxLayout()
        lalogin = QLabel("login : ")
        self.liLogin = QLineEdit()
        laepitech = QLabel("@epitech.eu")
        boxLoggin.addWidget(lalogin)
        boxLoggin.addWidget(self.liLogin)
        boxLoggin.addWidget(laepitech)

        boxPasswd = QHBoxLayout()
        lapasswd = QLabel("Passwd : ")
        self.liPasswd = QLineEdit()
        self.liPasswd.setEchoMode(QLineEdit.Password)
        boxPasswd.addWidget(lapasswd)
        boxPasswd.addWidget(self.liPasswd)

        btnConnect = QPushButton('Connexion', self)
        btnConnect.clicked.connect(self.on_click)

        vbox.addLayout(boxLoggin)
        vbox.addLayout(boxPasswd)
        vbox.addWidget(btnConnect)
        self.show()

    @pyqtSlot()
    def on_click(self):
        ret = self.reseau.authenticate(self.liLogin.text() + "@epitech.eu", self.liPasswd.text())
        if ret == True:
            self.win = GuiLesson(self.reseau)
            self.close()
        else:
            QMessageBox.warning("Connexion error", 'Error connexion, check id', QMessageBox.Ok, QMessageBox.Ok)


class GuiLesson(QWidget):
    def __init__(self, reseau):
        super().__init__()
        self.setGeometry(300, 300, 300, 220)
        self.setWindowTitle('Select cours')
        self.reseau = reseau
        planning = Planning()
        self.cours = planning.reqDay(reseau)
        self.showLesson()
        self.show()

    def showLesson(self):
        self.vbox = QHBoxLayout(self)
        self.combo1 = QComboBox()
        for cour in self.cours:
            self.combo1.addItem(cour._module + " " + cour._title)
        btnconnect = QPushButton("Select")
        btnconnect.clicked.connect(self.on_click)
        self.vbox.addWidget(self.combo1)
        self.vbox.addWidget(btnconnect)

    @pyqtSlot()
    def on_click(self):
        self.idCour = self.combo1.currentIndex()
        thread = Student(self.reseau, self.cours, self.idCour)
        thread.setStudentPresent()

    @pyqtSlot()
    def onFinished(self):
        print("finish")


class GuiShowStatus(QWidget) :
    def __init__(self):
        super().__init__()
        self.setGeometry(300, 300, 150, 100)
        self.setWindowTitle('status')
        title = QHBoxLayout()
        title.addWidget(QLabel('student'))
        title.addWidget(QLabel('status'))

        self.student = QHBoxLayout()
        self.login = QLabel()
        self.status = QLabel()
        self.student.addWidget(self.login)
        self.student.addWidget(self.status)

        qvbox = QVBoxLayout(self)
        qvbox.addLayout(title)
        qvbox.addLayout(self.student)
        self.show()

    def setStatus(self, login, status):
        self.login.setText(login)
        self.status.setText(status)
        print('login-> (' + login + ') status -> (' + status + ')')


class Student(QThread) :
    def __init__(self, reseau, cours, idcour):
        QThread.__init__(self, None)
        self.reseau = reseau
        self.cours = cours
        self.idCour = idcour
        self.gui = GuiShowStatus()
        self.run = True

    def __del__(self):
        self.run = False
        self.wait()

    def setStudentPresent(self):
        self.start()
        # Creation client com avec Serveur NFC
        print('thread start')
        client = Client(config.URI)
        try:
            lastID = ""
            while self.run:
                cardmonitor = CardMonitor()
                cardobserver = ComUsb()
                cardmonitor.addObserver(cardobserver)

                time.sleep(1)
                tmp = cardobserver.repUid
                print(tmp)
                if tmp != "" and tmp != lastID:
                    lastID = tmp
                    data = client.get('/1.0/user/byTag/' + tmp)
                    self.cours[self.idCour].setPresent(self.reseau, data["login"], "present")
                    self.gui.setStatus(data["login"], "present")

                cardmonitor.deleteObserver(cardobserver)
        except Exception as e:
            print(str(e))
            self.finished.emit()

    def Run(self, run):
        self.run = run


if __name__ == "__main__":
    app = QApplication(sys.argv)

    gui = GuiLogger()
    sys.exit(app.exec_())
