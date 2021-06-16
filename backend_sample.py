import cv2
import csv
import os
import pytesseract
import numpy as np
import datetime
from reportlab.pdfgen import canvas
import webbrowser

weekDays = ("MON","TUE","WED","THU","FRI","SAT","SUN")
today = datetime.date.today()
weekday = weekDays[today.weekday()]
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


config_file = os.getcwd()

student = {}
csvf = "D:/Programs/git/Attendee/bsc1.csv"
with open(csvf) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for row in csv_reader:
        student[row[1]] = row[0]

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
files = ['D:/Programs/git/Attendee/wotsapp.jpeg', 'D:/Programs/git/Attendee/wotsapp2.jpeg', 'D:/Programs/git/Attendee/wotsapp3.jpeg', 'D:/Programs/git/Attendee/wotsapp4.jpeg', 'D:/Programs/git/Attendee/wotsapp5.jpeg']
text = ""
for path in files:
    img = cv2.imread(path)
    text += pytesseract.image_to_string(img)

lines = text.split("\n")
students = list(student.keys())
present = {}
for i in lines:
    i = str(preprocessing(i)).strip()
    if i.isalnum() or i=="":
        continue
    for name in students:
        name = name.strip()
        try:
            if (name in i) or (i in name):
                print(name,student[name], " = ",i)
                present[name] = student[name]
                del student[name]
        except KeyError:
            continue

COOL_PDF_FILE = (csvf.split("/")[-1].split(".")[0]+" - "+weekday+"_"+str(today)+".pdf")

pdf = canvas.Canvas(COOL_PDF_FILE)
pdf.setTitle("Absentees"+weekday+"_"+str(today))
pdf.drawString(260, 800, "ABSENTEES")
x1 = 40
y = 780
for name,roll in student.items():
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
for name,roll in present.items():
    pdf.drawString(x1, y, roll)
    pdf.drawString(x1+70, y, name)
    y-=20
    if y<=60:
        y = 780
        x1 = 330
pdf.save()

webbrowser.open(COOL_PDF_FILE)
"""
with open(config_file + "\\absentees.csv", mode='w+',newline=None) as employee_file:
    employee_writer = csv.writer(employee_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    for name,roll in student.items():
        employee_writer.writerow([roll,name])
"""