from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from serialTread import ComMonitorThread
import serial.tools.list_ports_windows as comPortList
import queue
import io
import shutil

class ComboBox(QComboBox):
    popUpSignal = pyqtSignal()
    def showPopUp(self):
        self.popUpSignal.emit()
        super(ComboBox, self).showPopup()

class MainWindow(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        __BUTTON_SIZE = 50


        self.askTimer_delay = 500
        self.controllerId = 35031
        self.view = 6
        self.type = 0
        self.nessPos = [0, 0, 0, 0]

        self.messageType = "measure"

        self.cboxComPort = ComboBox()
        self.update_port_list()
        self.cboxComPort.popUpSignal.connect(self.update_port_list)

        self.btnConnect = QPushButton("Подключение")
        self.btnConnect.clicked.connect(self.onclick_connect)

        #self.lblId = QLabel("ID:")
        self.txtId = QLineEdit("35031")

        self.txtTimerPeriod = QLineEdit("200")
        self.btnStartTimer = QPushButton("Запуск")
        self.btnStopTimer = QPushButton("Остановка")
        self.btnStartTimer.clicked.connect(self.btnStartTimer_clicked)
        self.btnStopTimer.clicked.connect(self.btnStopTimer_clicked)


        self.cboxView = QComboBox()
        self.cboxView.addItems(["ВИД 2+2",
                                "ВИД 2+1",
                                "ВИД 1+2",
                                "ВИД 1+1",
                                "ВИД 0+2"
                                ])

        self.cboxType = QComboBox()
        self.cboxType.addItems(["РЕСИВЕР",
                                "КОМПРЕССОР"
                                ])

        self.lblPress_1 = QLabel("-----")
        self.btnUp_1 = QPushButton()
        self.btnUp_1.setIcon(QIcon('./assets/up.png'))
        self.btnUp_1.setIconSize(QSize(__BUTTON_SIZE, __BUTTON_SIZE))
        self.btnDown_1 = QPushButton()
        self.btnDown_1.setIcon(QIcon('./assets/down.png'))
        self.btnDown_1.setIconSize(QSize(__BUTTON_SIZE, __BUTTON_SIZE))

        self.lblPress_2 = QLabel("-----")
        self.btnUp_2 = QPushButton()
        self.btnUp_2.setIcon(QIcon('./assets/up.png'))
        self.btnUp_2.setIconSize(QSize(__BUTTON_SIZE, __BUTTON_SIZE))
        self.btnDown_2 = QPushButton()
        self.btnDown_2.setIcon(QIcon('./assets/down.png'))
        self.btnDown_2.setIconSize(QSize(__BUTTON_SIZE, __BUTTON_SIZE))

        self.lblPress_3 = QLabel("-----")
        self.btnUp_3 = QPushButton()
        self.btnUp_3.setIcon(QIcon('./assets/up.png'))
        self.btnUp_3.setIconSize(QSize(__BUTTON_SIZE, __BUTTON_SIZE))
        self.btnDown_3 = QPushButton()
        self.btnDown_3.setIcon(QIcon('./assets/down.png'))
        self.btnDown_3.setIconSize(QSize(__BUTTON_SIZE, __BUTTON_SIZE))

        self.lblPress_4 = QLabel("-----")
        self.btnUp_4 = QPushButton()
        self.btnUp_4.setIcon(QIcon('./assets/up.png'))
        self.btnUp_4.setIconSize(QSize(__BUTTON_SIZE, __BUTTON_SIZE))
        self.btnDown_4 = QPushButton()
        self.btnDown_4.setIcon(QIcon('./assets/down.png'))
        self.btnDown_4.setIconSize(QSize(__BUTTON_SIZE, __BUTTON_SIZE))


        self.lblStatus = QLabel("Статус")

        self.txtNessPos1 = QLineEdit("0")
        self.txtNessPos2 = QLineEdit("0")
        self.txtNessPos3 = QLineEdit("0")
        self.txtNessPos4 = QLineEdit("0")
        self.btnSendPreset = QPushButton("Отправить пресет")
        self.btnSendPreset.clicked.connect(self.btnSendPreset_clicked)
        self.btnStopPreset = QPushButton("Остановить пресет")
        self.btnStopPreset.clicked.connect(self.btnStopPreset_clicked)

        self.txtMessages = QTextEdit()


        self.gridL = QGridLayout()
        self.connectionLayout = QHBoxLayout()
        self.timersLayout = QHBoxLayout()
        self.presetLayout = QHBoxLayout()
        self.mainLayout = QVBoxLayout()

        self.connectionLayout.addWidget(self.cboxComPort)
        self.connectionLayout.addWidget(QLabel("ID:"))
        self.connectionLayout.addWidget(self.txtId)
        self.connectionLayout.addWidget(self.cboxView)
        self.connectionLayout.addWidget(self.cboxType)
        self.connectionLayout.addWidget(self.btnConnect)

        self.timersLayout.addWidget(QLabel("Период опроса"))
        self.timersLayout.addWidget(self.txtTimerPeriod)
        self.timersLayout.addWidget(self.btnStartTimer)
        self.timersLayout.addWidget(self.btnStopTimer)

        self.gridL.addWidget(self.lblPress_1,   0, 0, 1, 1, Qt.AlignCenter)
        self.gridL.addWidget(self.btnUp_1,      1, 0, 1, 1, Qt.AlignCenter)
        self.gridL.addWidget(self.btnDown_1,    2, 0, 1, 1, Qt.AlignCenter)

        self.gridL.addWidget(self.lblPress_2,   0, 1, 1, 1, Qt.AlignCenter)
        self.gridL.addWidget(self.btnUp_2,      1, 1, 1, 1, Qt.AlignCenter)
        self.gridL.addWidget(self.btnDown_2,    2, 1, 1, 1, Qt.AlignCenter)

        self.gridL.addWidget(self.lblPress_3,   0, 2, 1, 1, Qt.AlignCenter)
        self.gridL.addWidget(self.btnUp_3,      1, 2, 1, 1, Qt.AlignCenter)
        self.gridL.addWidget(self.btnDown_3,    2, 2, 1, 1, Qt.AlignCenter)

        self.gridL.addWidget(self.lblPress_4,   0, 3, 1, 1, Qt.AlignCenter)
        self.gridL.addWidget(self.btnUp_4,      1, 3, 1, 1, Qt.AlignCenter)
        self.gridL.addWidget(self.btnDown_4,    2, 3, 1, 1, Qt.AlignCenter)

        self.presetLayout.addWidget(QLabel("Предустановка"))
        self.presetLayout.addWidget(self.txtNessPos1)
        self.presetLayout.addWidget(self.txtNessPos2)
        self.presetLayout.addWidget(self.txtNessPos3)
        self.presetLayout.addWidget(self.txtNessPos4)
        self.presetLayout.addWidget(self.btnSendPreset)
        self.presetLayout.addWidget(self.btnStopPreset)


        self.mainLayout.addLayout(self.connectionLayout)
        self.mainLayout.addLayout(self.timersLayout)
        self.mainLayout.addLayout(self.gridL)
        self.mainLayout.addLayout(self.presetLayout)
        self.mainLayout.addWidget(self.txtMessages)
        self.mainLayout.addWidget(self.lblStatus, Qt.AlignLeft)

        self.setLayout(self.mainLayout)
        self.setWindowTitle("СИМУЛЯТОР")
        self.show()

        self.error_q = queue.Queue()

        self.monitor = None
        self.fileToWrite = None

        #self.stringIO_q = io.BytesIO()
        self.stringIO_q = queue.Queue()

        self.checkBuffertimer = QTimer()
        self.checkBuffertimer.timeout.connect(self.check_buffer)
        self.checkBuffertimer.start(100)

        self.askTimer = QTimer()
        self.askTimer.timeout.connect(self.timer_tick)

    def btnSendPreset_clicked(self):
        self.messageType = "send_preset"
        self.nessPos[0] = int(self.txtNessPos1.text())
        self.nessPos[1] = int(self.txtNessPos1.text())
        self.nessPos[2] = int(self.txtNessPos1.text())
        self.nessPos[3] = int(self.txtNessPos1.text())

    def btnStopPreset_clicked(self):
        self.messageType = "stop_preset"

    def btnStartTimer_clicked(self):
        try:
            self.askTimer_delay = int(self.txtTimerPeriod.text())
            self.askTimer.start(self.askTimer_delay)
        except:
            print("введите корректное время")

    def btnStopTimer_clicked(self):
        self.askTimer.stop()


    def check_buffer(self):
        try:
            s = self.stringIO_q.get(block=False, timeout=None)

            self.txtMessages.moveCursor(QTextCursor.End)
            self.txtMessages.insertPlainText(s)

            data = s.split(',')

            if data[0] == 'm':
                self.lblPress_1.setText(data[2])
                self.lblPress_2.setText(data[3])
                self.lblPress_3.setText(data[4])
                self.lblPress_4.setText(data[5])
        except:
            pass


    def timer_tick(self):
        valveStat = 0
        self.askTimer.stop()

        if self.btnUp_1.isDown():
            valveStat |= 0x01
        if self.btnDown_1.isDown():
            valveStat |= 0x02

        if self.btnUp_2.isDown():
            valveStat |= 0b00000100
        if self.btnDown_2.isDown():
            valveStat |= 0b00001000

        if self.btnUp_3.isDown():
            valveStat |= 0b00010000
        if self.btnDown_3.isDown():
            valveStat |= 0b00100000

        if self.btnUp_4.isDown():
            valveStat |= 0b01000000
        if self.btnDown_4.isDown():
            valveStat |= 0b10000000


        if self.messageType == "measure":
            sendMsg = "m,%d,%d,%c,\n" % (self.controllerId, self.view, chr(valveStat))
        elif self.messageType == "stop_preset":
            sendMsg = "sx,%d,\n" % self.controllerId
            self.messageType = "measure"
        elif self.messageType == "send_preset":
            sendMsg = "s,%05d,%d,%d,%d,%d,%d,%d,%d,\n" % (self.controllerId,
                                                          self.nessPos[0],
                                                          self.nessPos[1],
                                                          self.nessPos[2],
                                                          self.nessPos[3],
                                                          self.view,
                                                          self.type,
                                                          0)
            self.messageType = "measure"

        print("Message is: " + sendMsg, end="")

        if self.monitor is not None:
            self.txtMessages.moveCursor(QTextCursor.End)
            self.txtMessages.insertPlainText(">> " + sendMsg)
            self.monitor.send(sendMsg)
        self.askTimer.start(self.askTimer_delay)

    def onclick_connect(self):
        portName = self.cboxComPort.currentText()
        portBaud = 19200

        try:
            self.controllerId = int(self.txtId.text())
        except:
            self.controllerId = 35031

        #self.view = int(self.cboxView.currentText())
        if self.cboxView.currentText() == "ВИД 2+2":
            self.view = 6
        elif self.cboxView.currentText() == "ВИД 2+1":
            self.view = 5
        elif self.cboxView.currentText() == "ВИД 1+2":
            self.view = 4
        elif self.cboxView.currentText() == "ВИД 1+1":
            self.view = 3
        elif self.cboxView.currentText() == "ВИД 0+2":
            self.view = 2

        #self.type = int(self.cboxType.currentText())
        if self.cboxType.currentText() == "РЕСИВЕР":
            self.type = 0
        elif self.cboxType.currentText() == "КОМПРЕССОР":
            self.type = 1

        if self.monitor is None:
            self.monitor = ComMonitorThread(self.stringIO_q,
                                            self.error_q,
                                            portName,
                                            portBaud)
            print("monitor created")
            self.monitor.start()
            print("monitor started")
            com_error = self.error_q.get()[0]
            print("got status")
            if com_error is not "port error":
                print("not error status")
                self.lblStatus.setText("Port Connected")
                return

            self.lblStatus.setText("Connection error")

    def update_port_list(self):
        l = list()
        self.cboxComPort.clear()
        for p in comPortList.comports():
            l.append(p.device)
        self.cboxComPort.addItems(l)

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())
