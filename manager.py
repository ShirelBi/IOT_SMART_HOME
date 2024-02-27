# intended to manage the system that notifies for AirConditionerAlert  filters.
import paho.mqtt.client as mqtt
import time
import random
from mqtt_init import *
from icecream import ic
from datetime import datetime


def time_format():
    return f'{datetime.now()}  Manager|> '


ic.configureOutput(prefix=time_format)
ic.configureOutput(includeContext=False)  # use True for including script file context file


# Define callback functions
def on_log(client, userdata, level, buf):
    ic("log: " + buf)


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        ic("connected OK")
    else:
        ic("Bad connection Returned code= ", rc)


def on_disconnect(client, userdata, flags, rc=0):
    ic("DisConnected result code " + str(rc))


def on_message(client, userdata, msg):
    topic = msg.topic
    m_decode = str(msg.payload.decode("utf-8", "ignore"))
    ic("message from: " + topic, m_decode)

    # Extract the parameter values from the message
    humidity_value = float(m_decode.split('Humidity: ')[1].split()[0])
    temperature_value = float(m_decode.split('Temperature: ')[1].split()[0].replace("°C", ""))
    air_conditioner_status = m_decode.split('Air-Conditioner Status: ')[1].split()[0]
    on_off_status = m_decode.split('On/Off: ')[1].split()[0]

    # Check if any parameter exceeds its threshold and generate a specific alert message
    alert_messages = []
    if humidity_value < humidity_threshold_min or humidity_value > humidity_threshold_max:
        alert_messages.append(f"Humidity value ({humidity_value}) is out of range ({humidity_threshold_min}-{humidity_threshold_max})")

    if temperature_value < temperature_threshold_min or temperature_value > temperature_threshold_max:
        alert_messages.append(f"Temperature value ({temperature_value}°C) is out of range ({temperature_threshold_min}°C-{temperature_threshold_max}°C)")


    if alert_messages:
        alert_text = "ALERT: " + "; ".join(alert_messages) + ". Air-Conditioner turn ON"
        ic(alert_text + " " + m_decode)
        send_msg(client, warning_topic, alert_text)

    if on_off_status == 'ON':
        send_msg(client, button_topic, '{"value": 1}')

    if on_off_status == 'OFF':
        send_msg(client, button_topic, '{"value": 0}')    


def send_msg(client, topic, message):
    ic("Sending Message: " + message)
    client.publish(topic, message)


def client_init(cname):
    r = random.randrange(1, 10000000)
    ID = str(cname + str(r + 21))
    client = mqtt.Client(ID, clean_session=True)  # create new client instance
    # define callback function
    client.on_connect = on_connect  # bind callback function
    client.on_disconnect = on_disconnect
    client.on_log = on_log
    client.on_message = on_message
    if username != "":
        client.username_pw_set(username, password)
    ic("Connecting to broker ", broker_ip)
    client.connect(broker_ip, int(port))  # connect to broker
    return client


def main():
    cname = "Manager-"
    client = client_init(cname)
    # main monitoring loop
    client.loop_start()  # Start loop
    client.subscribe(comm_topic + 'iot_project/111')

    try:
        while conn_time == 0:
            time.sleep(conn_time + manag_time)
            ic(f"Time for sleep {conn_time + manag_time}")
            time.sleep(3)
        ic("con_time ending")
    except KeyboardInterrupt:
        client.disconnect()  # disconnect from broker
        ic("interrupted by keyboard")

    # Stop loop
    client.loop_stop()
    # end session
    client.disconnect()
    # disconnect from broker

    ic("End manager run script")

if __name__ == '__main__':
    main()