import sys
import os
import cv2
import csv
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication,QInputDialog,QFileDialog
import pytesseract
import numpy as np
import datetime
from reportlab.pdfgen import canvas
import webbrowser

entries = None
csv_file_name = None

def execution():
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

    # READ CSV FILE
    absent = {}
    csvf = csv_file_name
    with open(csvf) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            absent[row[1]] = row[0]

    # EXTRACT TEXT FROM IMAGE
    imgp = image_paths
    text = ""
    for path in imgp:
        img = cv2.imread(path)
        text += pytesseract.image_to_string(img)

    # CALCULATE THE ABSENTEE LIST
    lines = text.split("\n")
    students = list(absent.keys())
    present = {}
    for i in lines:
        i = str(preprocessing(i)).strip()
        if i.isalnum() or i=="":
            continue
        for name in students:
            name = name.strip()
            try:
                if (name in i) or (i in name):
                    present[name] = absent[name]
                    del absent[name]
            except KeyError:
                continue
    generate_pdf(csvf,present,absent)

def generate_pdf(csvf,present_dict,absent_dict):
    weekDays = ("MON","TUE","WED","THU","FRI","SAT","SUN")
    today = datetime.date.today()
    weekday = weekDays[today.weekday()]
    COOL_PDF_FILE = (csvf.split("/")[-1].split(".")[0]+" - "+weekday+"_"+str(today)+".pdf")

    pdf = canvas.Canvas(COOL_PDF_FILE)
    pdf.setTitle("Absentees"+weekday+"_"+str(today))
    pdf.drawString(260, 800, "ABSENTEES")
    x1 = 40
    y = 780
    for name,roll in absent_dict.items():
        pdf.drawString(x1, y, roll)
        pdf.drawString(x1+70, y, name)
        y-=20
        if y<=60:
            y = 780
            x1 = 330
    pdf.showPage()
    pdf.drawString(260, 800, "PRESENT")
    x1 = 40
    y = 780
    for name,roll in present_dict.items():
        pdf.drawString(x1, y, roll)
        pdf.drawString(x1+70, y, name)
        y-=20
        if y<=60:
            y = 780
            x1 = 330
    pdf.save()

    webbrowser.open(COOL_PDF_FILE)


def convert_upper_case(data):
    return np.char.upper(data)

def remove_punctuation(data):
    symbols = "!\"#$%&()*+-./:;<=>?@[\]^_`{|}~\n"
    for i in range(len(symbols)):
        data = np.char.replace(data, symbols[i], ' ')
        data = np.char.replace(data, "  ", " ")
    data = np.char.replace(data, ',', '')
    return data

def remove_apostrophe(data):
    return np.char.replace(data, "'", "")

def preprocessing(doc):
    doc = convert_upper_case(doc)
    doc = remove_punctuation(doc)
    doc = remove_apostrophe(doc)
    return doc


class TakeSS(QtWidgets.QMainWindow):
    def __init__(self):
        super(TakeSS, self).__init__()
        self.setupUi(self)

    def setupUi(self, Attendee):
        Attendee.setObjectName("Attendee")
        Attendee.resize(800, 600)
        Attendee.setStyleSheet("background-color: #1c1c1b;")
        self.centralwidget = QtWidgets.QWidget(Attendee)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(0, 20, 251, 141))
        self.label.setStyleSheet("")
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap("images/ATTENDEE.png"))
        self.label.setScaledContents(True)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(420, 450, 211, 51))
        self.pushButton_2.setStyleSheet("border: 1px solid white;\n"
"font: bold 18px Arial;\n"
"font-family: Arial;\n"
"color: white;\n"
"background-color: #1c1c1b;")
        self.pushButton_2.setObjectName("pushButton_2")
        self.nextButton = QtWidgets.QPushButton(self.centralwidget)
        self.nextButton.setGeometry(QtCore.QRect(700, 500, 91, 81))
        self.nextButton.setStyleSheet("border: none;")
        self.nextButton.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("images/right.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.nextButton.setIcon(icon)
        self.nextButton.setIconSize(QtCore.QSize(70, 70))
        self.nextButton.setObjectName("nextButton")
        self.listWidget = QtWidgets.QListWidget(self.centralwidget)
        self.listWidget.setGeometry(QtCore.QRect(160, 170, 471, 271))
        self.listWidget.setObjectName("listWidget")
        self.listWidget.setStyleSheet("QListWidget"
                                  "{"
                                  "text-align: center;"
                                  "border : 2px solid white;"
                                  "background : #1c1c1b;"
                                  "color : white;"
                                  "padding: 20px;"
                                  "}")

        Attendee.setCentralWidget(self.centralwidget)
        self.retranslateUi(Attendee)
        QtCore.QMetaObject.connectSlotsByName(Attendee)
        
        self.nextButton.clicked.connect(self.next)
        self.pushButton_2.clicked.connect(self.addss)
        items = self.listWidget.selectedItems()
        for item in items:
            item.setFlags(Qt.NoItemFlags)

    def retranslateUi(self, Attendee):
        _translate = QtCore.QCoreApplication.translate
        Attendee.setWindowTitle(_translate("Attendee", "MainWindow"))
        self.pushButton_2.setText(_translate("Attendee", "Add Screenshots"))
        
    def addss(self):
        global entries
        global image_paths
        file_ =QFileDialog()
        filter = "PNG (*.png);;JPEG (*.jpeg)"
        #filename = QFileDialog.getOpenFileName()
        file_.setFileMode(QFileDialog.ExistingFiles)
        image_paths = file_.getOpenFileNames(self, "Open files", "C\\Desktop", filter)
        image_paths = image_paths[0]
        entries = [name.split('/')[-1] for name in image_paths]
        for i in entries:
            lstItem = QtWidgets.QListWidgetItem(i)
            lstItem.setFlags(Qt.NoItemFlags)
            self.listWidget.addItem(lstItem)
        

    def next(self):
        if entries:
            widget.removeWidget(self)
            widget.addWidget(TakeCSV())
            widget.setCurrentIndex(widget.currentIndex() + 1)
        else:
            self.listWidget.setStyleSheet("QListWidget"
                                  "{"
                                  "text-align: center;"
                                  "border : 2px solid red;"
                                  "background : #1c1c1b;"
                                  "color : white;"
                                  "padding: 20px;"
                                  "}")


class TakeCSV(QtWidgets.QMainWindow):
    def __init__(self):
        super(TakeCSV, self).__init__()
        self.setupUi(self)
        
    def setupUi(self, Attendee):
        Attendee.setObjectName("Attendee")
        Attendee.resize(800, 600)
        Attendee.setStyleSheet("background-color: #1c1c1b;")
        self.centralwidget = QtWidgets.QWidget(Attendee)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(0, 20, 251, 141))
        self.label.setStyleSheet("")
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap("images/ATTENDEE.png"))
        self.label.setScaledContents(True)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(420, 410, 211, 51))
        self.pushButton_2.setStyleSheet("border: 1px solid white;\n"
"font: bold 18px Arial;\n"
"font-family: Arial;\n"
"color: white;\n"
"background-color: #1c1c1b;")
        self.pushButton_2.setObjectName("pushButton_2")
        self.nextButton = QtWidgets.QPushButton(self.centralwidget)
        self.nextButton.setGeometry(QtCore.QRect(700, 500, 91, 81))
        self.nextButton.setStyleSheet("border: none;")
        self.nextButton.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("images/right.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.nextButton.setIcon(icon)
        self.nextButton.setIconSize(QtCore.QSize(70, 70))
        self.nextButton.setObjectName("nextButton")
        self.backButton = QtWidgets.QPushButton(self.centralwidget)
        self.backButton.setGeometry(QtCore.QRect(10, 500, 91, 81))
        self.backButton.setStyleSheet("border: none;")
        self.backButton.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("images/left.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.backButton.setIcon(icon1)
        self.backButton.setIconSize(QtCore.QSize(70, 70))
        self.backButton.setObjectName("backButton")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(160, 210, 471, 191))
        self.label_2.setStyleSheet("border: 1px solid white;\n"
"font: bold 18px;\n"
"font-family: Arial;\n"
"color: white;\n"
"background-color: #1c1c1b;")
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        Attendee.setCentralWidget(self.centralwidget)

        self.retranslateUi(Attendee)
        QtCore.QMetaObject.connectSlotsByName(Attendee)
        
        self.backButton.clicked.connect(self.back)
        self.nextButton.clicked.connect(self.next)
        self.pushButton_2.clicked.connect(self.addcsv)

    def retranslateUi(self, Attendee):
        _translate = QtCore.QCoreApplication.translate
        Attendee.setWindowTitle(_translate("Attendee", "MainWindow"))
        self.pushButton_2.setText(_translate("Attendee", "Add CSV FILE"))
        self.label_2.setText(_translate("Attendee", "-"))

    def addcsv(self):
        global csv_file_name
        filter = "CSV (*.csv)"
        filename = QFileDialog()
        names = filename.getOpenFileNames(self, "Open files", "C\\Desktop", filter)
        csv_file_name = names[0][0]
        _translate = QtCore.QCoreApplication.translate
        self.label_2.setText(_translate("Attendee", csv_file_name.split("/")[-1]))


    def back(self):
        widget.removeWidget(self)
        widget.addWidget(TakeSS())
        widget.setCurrentIndex(widget.currentIndex() + 1)
    def next(self):
        if csv_file_name:
            widget.removeWidget(self)
            widget.addWidget(Wait())
            widget.setCurrentIndex(widget.currentIndex() + 1)
        else:
            self.label_2.setStyleSheet("border: 1px solid red;\n"
"font: bold 18px;\n"
"font-family: Arial;\n"
"color: white;\n"
"background-color: #1c1c1b;")

class Wait(QtWidgets.QMainWindow):
    def __init__(self):
        super(Wait, self).__init__()
        self.setupUi(self)
    def setupUi(self, Attendee):
        Attendee.setObjectName("Attendee")
        Attendee.resize(800, 600)
        Attendee.setStyleSheet("background-color: #1c1c1b;")
        self.centralwidget = QtWidgets.QWidget(Attendee)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(0, 20, 251, 141))
        self.label.setStyleSheet("")
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap("images/ATTENDEE.png"))
        self.label.setScaledContents(True)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(220, 270, 331, 51))
        self.label_2.setStyleSheet("border: none;\n"
"font: bold 18px;\n"
"font-family: Arial;\n"
"color: white;\n"
"background-color: #1c1c1b;")
        self.label_2.setObjectName("label_2")
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        Attendee.setCentralWidget(self.centralwidget)

        self.retranslateUi(Attendee)
        QtCore.QMetaObject.connectSlotsByName(Attendee)
        
        QtCore.QTimer.singleShot(10, lambda: self.exit())

    def retranslateUi(self, Attendee):
        _translate = QtCore.QCoreApplication.translate
        Attendee.setWindowTitle(_translate("Attendee", "MainWindow"))
        self.label_2.setText(_translate("Attendee", "EXECUTING PROGRAM...."))

    def exit(self):
        execution()
        widget.removeWidget(self)
        widget.addWidget(TakeSS())
        widget.setCurrentIndex(widget.currentIndex() + 1)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = QtWidgets.QStackedWidget()
    start_window = TakeSS()
    widget.addWidget(start_window)
    widget.setFixedHeight(600)
    widget.setFixedWidth(800)
    widget.show()
    sys.exit(app.exec_())
