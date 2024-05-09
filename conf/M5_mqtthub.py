from datetime import datetime
from paho.mqtt import client as mqtt
import json
import random

from conf.公共信息 import json_path, gateway_address

topic = f'LXIH/DataChange/{gateway_address}'
client_id = 'python-mqtt-{}'.format(random.randint(0, 1000))


def on_connect(client, userdata, flags, rc):
    """一旦连接成功, 回调此方法"""
    rc_status = ["连接成功", "协议版本错误", "无效的客户端标识", "服务器无法使用", "用户名或密码错误", "无授权"]
    # print("connect：", rc_status[rc])


def connect_mqtt():
    mqttclient = mqtt.Client(client_id)
    mqttclient.on_connect = on_connect
    MQTTHOST = '1.95.10.23'
    MQTTPORT = 1883
    mqttclient.connect(MQTTHOST, MQTTPORT, 60)
    mqttclient.loop_start()

    return mqttclient


def publish():
    mqttClient = connect_mqtt()

    with open(F'{json_path}', 'r', encoding='utf-8') as file:
        # current_time = datetime.now()
        # year = current_time.year
        # month = current_time.month
        # target_time = current_time.replace(year=year, month=month)
        # timestamp = int(target_time.timestamp())

        data = json.load(file)
        # data['timestamp'] = timestamp
        json_str = json.dumps(data)
    msg = json_str
    mqttClient.publish(topic=topic, payload=msg)
    mqttClient.loop_stop()


if __name__ == '__main__':
    publish()

