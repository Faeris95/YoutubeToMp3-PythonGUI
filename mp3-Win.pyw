#!/usr/bin/python3
# -- coding: utf-8 --
# coding: utf-8
import os, sys, glob, time, shlex, subprocess, shutil, threading
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QThread
from PyQt5.QtCore import QSize
from PyQt5.QtCore import pyqtSignal


"""Written by Faeris95 2015"""
"""For any question/help : sebastien.rolland@protonmail.com"""

i = 0
j = 0


class Music:
    def __init__(self, adr,i):
        self.nom = None
        self.setAdr(adr)
        self.state = 'En attente'
        self.i = i
        
    def getName(self):
        if(self.nom):
        	return self.nom
        else:
        	return self.adr

    def getState(self):
        return self.state
    def getIndex(self):
    	return self.i

    def setState(self, state):
        self.state = state

    def getAdr(self):
        return self.adr
    def setNom(self, nom):
    	self.nom = nom

    def setAdr(self, adr):
        self.adr = adr
        
class TitleThread(QThread):
	
	sig = pyqtSignal(Music)
	def __init__(self, parent  = None):
		super(TitleThread, self).__init__(parent)
		self.musicList = []
		self.currentDir = os.path.dirname(os.path.realpath(__file__))

	def add(self, music):
		self.musicList.append(music)

	def run(self):
		while(self.musicList):
			self.music = self.musicList.pop(0)
			nom = self.recup_titre()
			self.music.setNom(nom)
			self.sig.emit(self.music)

	def __del__(self):
		self.wait()

	def recup_titre(self):
		return os.popen(self.currentDir+'\\youtube-dl.exe -e ' + self.music.getAdr(), 'r').read().rstrip()


class mySignal():
	def __init__(self, nb, state):
		self.nb = nb
		self.state = state
	def getNb(self):
		return self.nb
	def getState(self):
		return self.state

class DownloaderThread(QThread):
	sig = pyqtSignal(mySignal)
	def __init__(self, parent = None):
		super(DownloaderThread, self).__init__(None)
		self.parent = parent
	def addDownloader(self, download):
		self.download = download
	def addList(self, liste):
		self.liste = liste
	def addWidgetsList(self, liste):
		self.widget_list = liste

	def run(self):
		i=0
		for music in self.liste:
			music.setState("En cours")
			self.sig.emit(mySignal(i,"En cours"))
			result = self.download.download(music.getAdr())
			if (result != 0):
				self.sig.emit(mySignal(-2,-2))
				
			else:
				music.setState("Téléchargé")
				self.sig.emit(mySignal(i,"Téléchargé"))
				
			i += 1
		self.sig.emit(mySignal(-1,-1))

	def __del__(self):
		self.wait()




class Downloader:
    def __init__(self):
        self.tableau = []
        self.liste = ['\\Musique', '\\Musiques', '\\Music', '\\Musics', '\\Musik', '\\Musiks']
        self.chemin = "C:"+os.environ["HOMEPATH"]
        self.currentDir = os.path.dirname(os.path.realpath(__file__))
        mp3 = self.currentDir+"\\youtube-dl.exe -q -x --audio-format mp3"
        self.mp3 = shlex.split(mp3)
        self.mp3[0]=self.currentDir+"\\youtube-dl.exe"

        self.mp3.append('')
    def youtube_dl_MAJ(self):
        maj = os.popen(self.currentDir+'\\youtube-dl.exe --update', 'r').read()
        if 'setup.py' in maj:
            print("Unable to update youtube-dl, you have to do it manually using your package manager")
        elif 'up-to-date' in maj:
            print('Youtube-dl is up-to-date')
        else:
            print('Either youtube-dl has been updated or a problem has been encountered')
        print("")


    def check_for_location(self):
        global i
        global j
        if not os.path.exists(self.currentDir + "\\.pythdownloader"):
            os.mkdir(self.currentDir + "\\.pythdownloader")
            fichier = open(self.currentDir + "\\.pythdownloader\\pythdownloader.conf", 'w')
            fichier.close()
        os.chdir(self.currentDir + "\\.pythdownloader")
        fichier = open(self.currentDir + "\\.pythdownloader\\pythdownloader.conf", 'r')
        ligne = fichier.read()
        fichier.close()
        if (ligne != ""):
            self.chemin = ligne
            print(self.chemin)
            fichier.close()
        else:
            lenght = len(self.liste)
            while (i < lenght):
                print(self.chemin + self.liste[i])
                if os.path.exists(self.chemin + self.liste[i]):

                    self.chemin += self.liste[i]
                    break
                i += 1
            if (i == lenght):
                i = 0
                while (i < lenght):
                    if os.path.exists(self.chemin + self.liste[i].lower()):
                        self.chemin += self.liste[i].lower()
                        break
                    i += 1

            if (i == lenght):
                i = 0
                while (i < lenght):
                    if os.path.exists(self.chemin + self.liste[i].upper()):
                        self.chemin += self.liste[i].upper()
                        break
                    i += 1
            if (i==lenght):
                os.mkdir(self.chemin + '\\Musique')
                self.chemin += '\\Musique'
        self.fichier = open(self.currentDir + "\\.pythdownloader\\pythdownloader.conf", 'w')
        self.fichier.write(self.chemin)
        self.fichier.close()
        self.chemin += '\\'
        return self.chemin

    def changer_chemin(self, txt):
        self.chemin = txt
        self.fichier = open(self.currentDir+ "\\.pythdownloader\\pythdownloader.conf", 'w')
        self.fichier.write(self.chemin)
        self.fichier.close()
        self.chemin += "\\"

    def download(self, adr):

        if 'index' in adr:
            adr = adr[0:adr.find('&index')]
        if 'list' in adr:
            adr = adr[0:adr.find('&list')]
        self.mp3[5] = adr
        print(self.mp3)
        a = subprocess.run(self.mp3, creationflags = 0x08000000,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        print(a)
        a=a.returncode
        if (a == 0):
            self.fichier = glob.glob('*.mp3')
            shutil.move(self.fichier[0], self.chemin + self.fichier[0][:-16] + '.mp3')
            return a
        else:
            return a


class UI(QtWidgets.QMainWindow):
    def __init__(self):
        super(UI, self).__init__()

        self.i = 0
        self.music_list = []
        self.widget_list = []
        self.widget_listTxt = []
        self.a = Downloader()
        self.tabListe = None
        self.Thread = TitleThread()
        self.Thread.sig[Music].connect(self.update)
        self.DThread = DownloaderThread(self)
        self.DThread.sig[mySignal].connect(self.finish)

        self.initUI()
        

    def initUI(self):
        self.center()
        self.setFixedSize(800, 400)
        self.txt = QtWidgets.QLineEdit(self)
        self.txt.resize(600, 20)
        self.txt.move(10, 330)
        self.currentDir=os.path.dirname(os.path.realpath(__file__))
        line = QtWidgets.QFrame(self)
        line.setGeometry(QtCore.QRect(650, 0, 1, 400))
        line.setFrameShape(QtWidgets.QFrame.StyledPanel)
        line.setFrameShadow(QtWidgets.QFrame.Raised)

        self.tabListe = QtWidgets.QTableWidget(0, 2, self)
        self.tabListe.setColumnWidth(0, 450)
        self.tabListe.setColumnWidth(1, 150)
        self.tabListe.setFixedSize(600, 250)
        self.tabListe.move(10, -1)
        self.tabListe.verticalHeader().hide()
        self.tabListe.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        self.tabListe.horizontalScrollBar().setDisabled(True)
        self.tabListe.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        lst = ["Titre", "État"]
        self.tabListe.setHorizontalHeaderLabels(lst)
        self.btn_telech = QtWidgets.QPushButton('Télécharger', self)
        self.btn_telech.resize(100, 20)
        self.btn_telech.move(680, 300)

        btn_quitter = QtWidgets.QPushButton('Quitter', self)
        btn_quitter.resize(100, 20)
        btn_quitter.move(680, 360)
        btn_quitter.clicked.connect(QtCore.QCoreApplication.instance().quit)
        self.btn_entre = QtWidgets.QPushButton('Ajouter', self)
        self.btn_entre.resize(100, 20)
        self.btn_entre.move(680, 330)

        lbl_telech = QtWidgets.QLabel('Insérez un lien :', self)
        lbl_telech.move(10, 300)

        lbl_chemin = QtWidgets.QLabel("Chemin de destination : ", self)
        lbl_chemin.resize(150, 20)
        lbl_chemin.move(10, 260)
        self.chemTxt = QtWidgets.QLineEdit(self.a.check_for_location(), self)
        self.chemTxt.resize(447, 20)
        self.chemTxt.move(163, 260)

        self.btn_changer = QtWidgets.QPushButton("Changer", self)
        self.btn_changer.resize(100, 20)
        self.btn_changer.move(680, 260)

        self.btn_telech.clicked.connect(lambda: self.telecharger())
        self.btn_changer.clicked.connect(lambda: self.changer_chemin())
        self.btn_entre.clicked.connect(lambda: self.ajouterEntree())
        self.verify()
        self.setWindowTitle('PythDownloader 1.1')
        self.show()

    def enable_Widget(self, button):
        for but in button:
            but.setEnabled(True)

    def disable_Widget(self, button):
        for but in button:
            but.setEnabled(False)

    def telecharger(self):
        button = [self.btn_telech, self.btn_changer, self.btn_entre]
        self.disable_Widget(button)
        self.DThread.addDownloader(self.a)
        self.DThread.addList(self.music_list)
        self.DThread.addWidgetsList(self.widget_list)
        self.DThread.start()

    def finish(self, signal):
        if(signal.getNb() == -2):
            QMessageBox.critical(self, "Erreur","Erreur lors du téléchargement, lien erroné ou youtube-dl n'est pas à jour")
            QtCore.QCoreApplication.instance().quit
        elif(signal.getNb() > -1):
            self.widget_list[signal.getNb()].setText(signal.getState())
            QtWidgets.QApplication.processEvents()
        else:
            self.enable_Widget([self.btn_changer, self.btn_telech, self.btn_entre])
            QMessageBox.information(self, "Terminé", "Toutes les musiques ont été téléchargées !")

    def verify(self):
        os.chdir("..")
        if not (os.path.exists(os.path.dirname(os.path.realpath(__file__))+'\\youtube-dl.exe')):
            print(os.path.dirname(os.path.realpath(__file__))+'\\youtube-dl.exe')
            QMessageBox.critical(self, "Erreur", "PythDownloader necessite youtube-dl")
            QtCore.QCoreApplication.instance().quit

    def changer_chemin(self):
        file = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Sélectionnez un dossier"))
        self.a.changer_chemin(file)
        self.chemTxt.setText(file)

    def clear_txt(self):
        self.txt.clear()

    def ajouterEntree(self):
        txt = self.txt.text()

        self.clear_txt()
        if (txt == ""):
            QMessageBox.warning(self, "Erreur d'entrée", "Il n'y a aucun lien !")
        elif not ("youtube" in txt):
            QMessageBox.warning(self, "Erreur d'entrée", "Insérez un lien de youtube !")
        else:
            music = Music(txt,self.i)
            new = QtWidgets.QTableWidgetItem()
            new2 = QtWidgets.QTableWidgetItem()
            new2.setFlags(QtCore.Qt.ItemIsEnabled)
            new.setFlags(QtCore.Qt.ItemIsEnabled)
            new.setText(music.getName())
            new2.setText(music.getState())
            self.tabListe.setRowCount(self.i + 1)
            self.tabListe.setItem(self.i, 0, new)
            self.tabListe.setItem(self.i, 1, new2)
            self.i += 1
            self.music_list.append(music)
            self.widget_list.append(new2)
            self.widget_listTxt.append(new)
            self.Thread.add(music)
            self.Thread.start()


    def center(self):
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def update(self, music):
        self.widget_listTxt[music.getIndex()].setText(music.getName())
        self.widget_list[music.getIndex()].setText(music.getState())


def main():
    app = QtWidgets.QApplication(sys.argv)
    ex = UI()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
