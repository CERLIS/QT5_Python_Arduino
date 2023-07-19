

from PyQt5 import QtWidgets, uic
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtCore import QIODevice
from pyqtgraph import PlotWidget
import pyqtgraph
import sys

app = QtWidgets.QApplication([])
ui = uic.loadUi('design.ui')
ui.setWindowTitle("SerialGUI")

serial = QSerialPort()
serial.setBaudRate(9600)

portList = []
ports = QSerialPortInfo().availablePorts()
for port in ports:
    portList.append(port.portName())
print(portList)
ui.comL.addItems(portList)

list_data = ''
posX = 100
posY = 100
srtmpB = 3.3 #значение для фильтрации на экране
listX = []#список для графика
for x in range(100): listX.append(x)
listY = []#список для графика
for y in range(100): listY.append(0)
def onRead():
    global list_data

    data = '\n'
    rx = serial.readLine() #чтение данных из порта Экспонтенциальное бегущее среднее
    list_data += str(rx, 'utf-8')
    if data in list_data:

        rxs = list_data.strip()
        data = rxs.split('#')
        print(data)

        if len(data) == 4:

            global srtmpB
            srtmpB += (float(data[0]) - srtmpB)*0.1
            srtmpB = round(srtmpB,2)

            print(srtmpB)

            ui.tempB.setValue(int(srtmpB*10))
            ui.tempL.setText(str(srtmpB))
            if abs(float(data[3]) - float(data[0])) < 0.1: ui.circle.setChecked(True)#включать кружок если рядом с установленным напряженикм
            else: ui.circle.setChecked(False)
            global posX
            global posY
            posX = int(float(data[0])*100)
            posY = int(float(data[3]) * 100)
            ui.circle.setGeometry(posX, posY, 20, 20)

            #заполнение графика
            global listX, listY
            listY = listY[1:]
            listY.append(srtmpB)
            ui.graph.clear()
            ui.graph.plot(listX,listY)
        elif len(data) == 5:# пакет от контроллера с установленным выходным напряжением
            ui.lcdN.display(float(data[4]))#вывод информации на большой циферблад.


        list_data = ''







# функция для пеердачи данных в сериал
def serialSend(data): #список int
    txs = ''
    for val in data:
        txs += str(val)


    serial.write(txs.encode()) # отправляем в порт сначала превратив в байты

def onOpen():
    serial.setPortName(ui.comL.currentText())#выявить выбранный порт в combbox
    serial.open(QIODevice.ReadWrite)#открыть выбранный порт


def onClose():
    serial.close()#закрытие порта

def ledControl(val): #отправка значения с галочки LED
    if val == 2: val = 1;
    if val == 0: val = 3.3
    serialSend([4, val])

def fanControl(val): #отправка значения с галочек FUN
    if val == 2: val = 77;
    if val == 0: val = 10
    serialSend([2, val])


def bulbControl(val): #отправка значения с галочек BULT
    if val == 2: val = 88;
    serialSend([3, val])

def RGBcontrol(): #отправка значений с ползунков
    serialSend([1, ui.RS.value()])
    serialSend([2, ui.GS.value()])
    serialSend([3, ui.BS.value()])

def servoControl(val): #отправка значенмй с крутилки
    serialSend([4, val/10])
    print(val)

def sendText(): #отправка занчения из текстового поля
    txs = '4'
    data = (ui.textF.displayText())
    print(data)

    try:
        if float(data) <= 5:


            print(data)
            txs += ui.textF.displayText()
            serial.write(txs.encode())


        else:
            txs += '3.3'
            serial.write(txs.encode())
            ui.lcdN.display('error')


    except:
        print('error')
        ui.lcdN.display('0000')






serial.readyRead.connect(onRead)

# def test():
#     print('kek')
# # ui.comL.currentIndexChanged.connect(ui.comL.clear) #очистка комба бокса
# ui.comL.currentIndexChanged.connect(test)# проверка работы функции изменение порта
# ui.openB.clicked.connect(test) #нажатие на кнопку open
ui.openB.clicked.connect(onOpen) #нажатие на кнопку open
ui.closeB.clicked.connect(onClose) #нажатие на кнопку close
ui.ledC.stateChanged.connect(ledControl)#обработка кнопки led
ui.fanC.stateChanged.connect(fanControl) #обработка кнопки fan
ui.bulbC.stateChanged.connect(bulbControl) #обработка кнопки bulb

ui.RS.valueChanged.connect(RGBcontrol) #ПОЛЗУНКИ
ui.GS.valueChanged.connect(RGBcontrol) #ПОЛЗУНКИ
ui.BS.valueChanged.connect(RGBcontrol) #ПОЛЗУНКИ

ui.servoK.valueChanged.connect(servoControl) #КРУТИЛКА

ui.sendB.clicked.connect(sendText)


# vals = [10, 11, 12] # тест функции serialSend
# serialSend(vals)


ui.show()
app.exec()