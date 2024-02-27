import sys
import random
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import paho.mqtt.client as mqtt
from mqtt_init import *
from DHT import read_dht_temperature, read_dht_humidity, DHT_topic
import matplotlib.pyplot as plt
import time
from AppDatabase import *


global CONNECTED, humidity_, temperature_, conditioner_status_, onOff_status_

CONNECTED = False
r = random.randrange(1, 10000000)

# Creating Client name - should be unique
clientname = "AirConditionerAlert"+str(r)
AirConditionerAlert_topic = 'pr/home/AirConditionerAlert/iot_project/111'

update_rate = 1500  # in msec

# Call the init_db function to create the database and table if they don't exist
init_db()


class Mqtt_client():

    def __init__(self):
        # broker IP adress:
        self.broker=''
        self.topic=''
        self.port=''
        self.clientname=''
        self.username=''
        self.password=''
        self.subscribeTopic=''
        self.publishTopic=''
        self.publishMessage=''
        self.on_connected_to_form = ''
        self.on_message_callback = None

    # Setters and getters
    def set_on_connected_to_form(self,on_connected_to_form):
        self.on_connected_to_form = on_connected_to_form

    def get_broker(self):
        return self.broker

    def set_broker(self, value):
        self.broker = value

    def get_port(self):
        return self.port

    def set_port(self, value):
        self.port = value

    def get_clientName(self):
        return self.clientName

    def set_clientName(self, value):
        self.clientName = value

    def get_username(self):
        return self.username

    def set_username(self, value):
        self.username = value

    def get_password(self):
        return self.password

    def set_password(self, value):
        self.password = value

    def get_subscribeTopic(self):
        return self.subscribeTopic

    def set_subscribeTopic(self, value):
        self.subscribeTopic = value

    def get_publishTopic(self):
        return self.publishTopic

    def set_publishTopic(self, value):
        self.publishTopic = value

    def get_publishMessage(self):
        return self.publishMessage

    def set_publishMessage(self, value):
        self.publishMessage = value


    def on_log(self, client, userdata, level, buf):
        print("log: "+buf)

    def set_on_message_callback(self, callback):
        self.on_message_callback = callback

    def on_connect(self, client, userdata, flags, rc):
        global CONNECTED
        if rc == 0:
            print("connected OK")
            CONNECTED = True
            self.on_connected_to_form()
            self.subscribe_to(DHT_topic)
        else:
            print("Bad connection Returned code=", rc)

    def on_disconnect(self, client, userdata, flags, rc=0):
        CONNECTED = False
        print("DisConnected result code "+str(rc))

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        m_decode = str(msg.payload.decode("utf-8", "ignore"))
        print("message from:" + topic, m_decode)
        if self.on_message_callback:
            self.on_message_callback(m_decode)
        else:
            mainwin.subscribeDock.update_mess_win(m_decode)

    def connect_to(self):
        # Init paho mqtt client class
        self.client = mqtt.Client(self.clientname, clean_session=True) # create new client instance
        self.client.on_connect=self.on_connect  #bind call back function
        self.client.on_disconnect=self.on_disconnect
        self.client.on_log = self.on_log
        self.client.on_message=self.on_message
        self.client.username_pw_set(self.username,self.password)
        print("Connecting to broker ",self.broker)
        self.client.connect(self.broker,self.port)     #connect to broker

    def disconnect_from(self):
        self.client.disconnect()

    def start_listening(self):
        self.client.loop_start()

    def stop_listening(self):
        self.client.loop_stop()

    def subscribe_to(self, topic):
        if CONNECTED:
            self.client.subscribe(topic)
            print(f"Subscribed to topic: {topic}")  # Debugging line
        else:
            print("Can't subscribe. Connection should be established first")

    def publish_to(self, topic, message):
        if CONNECTED:
            self.client.publish(topic, message)
        else:
            print("Can't publish. Connecection should be established first")

class ConnectionDock(QDockWidget):
    """Main """
    def __init__(self,mc):
        QDockWidget.__init__(self)

        self.mc = mc
        self.mc.set_on_connected_to_form(self.on_connected)
        self.eHostInput=QLineEdit()
        self.eHostInput.setInputMask('999.999.999.999')
        self.eHostInput.setText(broker_ip)

        self.ePort=QLineEdit()
        self.ePort.setValidator(QIntValidator())
        self.ePort.setMaxLength(4)
        self.ePort.setText(broker_port)

        self.eClientID=QLineEdit()
        global clientname
        self.eClientID.setText(clientname)

        self.eUserName=QLineEdit()
        self.eUserName.setText(username)

        self.ePassword=QLineEdit()
        self.ePassword.setEchoMode(QLineEdit.Password)
        self.ePassword.setText(password)

        self.eKeepAlive=QLineEdit()
        self.eKeepAlive.setValidator(QIntValidator())
        self.eKeepAlive.setText("60")

        self.eSSL=QCheckBox()

        self.eCleanSession=QCheckBox()
        self.eCleanSession.setChecked(True)

        self.eConnectbtn=QPushButton("Enable/Connect", self)
        self.eConnectbtn.setToolTip("click me to connect")
        self.eConnectbtn.clicked.connect(self.on_button_connect_click)
        self.eConnectbtn.setStyleSheet("background-color: gray")

        self.ePublisherTopic=QLineEdit()
        self.ePublisherTopic.setText(AirConditionerAlert_topic)

        # restart values
        self.Humidity = QLineEdit()
        self.Humidity.setText('')

        self.Temperature = QLineEdit()
        self.Temperature.setText('')

        self.ConditionerStatus = QLineEdit()
        self.ConditionerStatus.setText('')

        self.OnOff = QLineEdit()
        self.OnOff.setText('')

        gridLayout = QGridLayout()

        gridLayout.addWidget(QLabel("Turn On/Off"), 0, 0)
        gridLayout.addWidget(self.eConnectbtn, 0, 1)
        gridLayout.addWidget(QLabel("Pub topic"), 1, 0)
        gridLayout.addWidget(self.ePublisherTopic, 1, 1)
        gridLayout.addWidget(QLabel("Humidity"), 2, 0)
        gridLayout.addWidget(self.Humidity, 2, 1)
        gridLayout.addWidget(QLabel("Temperature"), 3, 0)
        gridLayout.addWidget(self.Temperature, 3, 1)
        gridLayout.addWidget(QLabel("On/Off"), 4, 0)
        gridLayout.addWidget(self.OnOff, 4, 1)
        gridLayout.addWidget(QLabel("Air-Conditioner Status"), 5, 0)
        gridLayout.addWidget(self.ConditionerStatus, 5, 1)

        gridLayout.setContentsMargins(10, 10, 10, 10)
        gridLayout.setHorizontalSpacing(10)
        gridLayout.setVerticalSpacing(10)

        widget = QWidget(self)
        widget.setLayout(gridLayout)

        self.setTitleBarWidget(widget)
        self.setTitleBarWidget(widget)
        self.setWidget(widget)
        self.setWindowTitle("Smart Aquarium Filter Monitor")

    def on_connected(self):
        global CONNECTED
        if CONNECTED:
            self.eConnectbtn.setStyleSheet("background-color: #4CAF50;")
            self.eConnectbtn.setText("Press to Disable/Disconnect")
        else:
            self.eConnectbtn.setStyleSheet("background-color: red")
            self.eConnectbtn.setText("Press to Enable/Connect")

    def on_button_connect_click(self):
        global CONNECTED

        if not CONNECTED:
            self.mc.set_broker(self.eHostInput.text())
            self.mc.set_port(int(self.ePort.text()))
            self.mc.set_clientName(self.eClientID.text())
            self.mc.set_username(self.eUserName.text())
            self.mc.set_password(self.ePassword.text())
            self.mc.connect_to()
            self.mc.start_listening()

        else:
            self.mc.stop_listening()
            self.mc.disconnect_from()

        CONNECTED = not CONNECTED
        self.on_connected()

    def push_button_click(self):
        self.mc.publish_to(self.ePublisherTopic.text(), '"value":1')


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        # Init of Mqtt_client class
        self.mc = Mqtt_client()

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_data)
        self.timer.start(update_rate) # in msec

        # general GUI settings
        self.setUnifiedTitleAndToolBarOnMac(True)

        # set up main window
        self.setGeometry(30, 600, 450, 180)
        self.setWindowTitle('AirConditionerAlert')

        # Init QDockWidget objects
        self.connectionDock = ConnectionDock(self.mc)

        self.addDockWidget(Qt.TopDockWidgetArea, self.connectionDock)

        self.initial_update = True
        self.mc.set_on_message_callback(self.on_dht_message)

        self.received_temperature = None

        self.last_plot_time = time.time()

    @staticmethod
    def plot_data():
        data = fetch_data()

        timestamps = []
        humidity_values = []
        temperatures = []

        for message, timestamp in data:
            parts = message.split()
            humidity = float(parts[1])
            temperature = float(parts[3][:-2])

            timestamps.append(timestamp)
            humidity_values.append(humidity)
            temperatures.append(temperature)

        fig, ax = plt.subplots(2, sharex=True, figsize=(10, 8))
        fig.autofmt_xdate()

        ax[0].plot(timestamps, humidity_values, label='humidity')
        ax[0].set_title('Humidity')

        ax[1].plot(timestamps, temperatures, label='Temperature (°C)')
        ax[1].set_title('Temperature (°C)')

        ax[0].set_xticklabels([])
        ax[1].set_xticklabels([])

        plt.show()

    def read_humidity(self):
        return read_dht_humidity()

    def read_temperature(self):
        return read_dht_temperature()

    def on_dht_message(self, message):
        print(f"Received DHT message: {message}")

        # Parse the temperature value from the message
        message_parts = message.split()
        temp = float(message_parts[1])  # Assuming the message format is "Temperature: 25.0 Humidity: 50.0"

        # Set the received_temperature value
        self.received_temperature = temp

    def update_data(self, temperature=None, humidity=None):
        if not CONNECTED or not self.initial_update:
            self.connectionDock.Humidity.setText('')
            self.connectionDock.Temperature.setText('')
            self.connectionDock.OnOff.setText('')
            self.connectionDock.ConditionerStatus.setText('')
            return

        print('Next update')

        # Update the values of humidity, temperature according to your sensor readings
        humidity_ = self.read_humidity()
        temperature_ = self.received_temperature if self.received_temperature is not None else self.read_temperature()

        # Check if all parameters are valid and set filter status accordingly
        if self.is_valid_humidity(humidity_) and self.is_valid_temperature(temperature_):
            conditioner_status_ = "OK"
            onOff_status_ = "OFF"
            
        else:
            conditioner_status_ = "Warning"
            onOff_status_ = "ON"

        # Update the GUI and publish the data
        current_data = f'Humidity: {humidity_} Temperature: {temperature_}°C Air-Conditioner Status: {conditioner_status_} On/Off: {onOff_status_}'
        self.connectionDock.Humidity.setText(str(humidity_))
        self.connectionDock.Temperature.setText(str(temperature_))
        self.connectionDock.ConditionerStatus.setText(conditioner_status_)
        self.connectionDock.OnOff.setText(onOff_status_)
        self.mc.publish_to(AirConditionerAlert_topic, current_data)

        save_message(current_data)

        # Call plot_data() once every 10 seconds
        current_time = time.time()
        if current_time - self.last_plot_time >= 15:
            self.plot_data()
            self.last_plot_time = current_time
    def is_valid_humidity(self, humidity):
        return humidity_threshold_min <= humidity <= humidity_threshold_max

    def is_valid_temperature(self, temperature):
        return temperature_threshold_min <= temperature <= temperature_threshold_max

app = QApplication(sys.argv)

stylesheet = """
    QMainWindow {
        background-color: #d1d1e0;
    }
    QLineEdit {
        border: 1px solid #C0C0C0;
        padding: 5px;
    }
    QPushButton {
        background-color: #6E9FEC;
        color: white;
        padding: 6px 12px;
        text-align: center;
        font-size: 14px;
        margin: 4px 2px;
        border-radius: 5px;
    }
    QPushButton:hover {
        background-color: #5683D3;
    }
    QLabel {
        font-size: 14px;
        font-family: "Segoe UI";
    }

"""
app.setStyleSheet(stylesheet)

mainwin = MainWindow()
mainwin.show()
app.exec_()
