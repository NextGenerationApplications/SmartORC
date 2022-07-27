import json
import logging
from json import dumps, loads

from kafka import KafkaProducer, KafkaConsumer

logging.basicConfig(level=logging.INFO)


class Producer:
    def send_message(self, topic, data):
        list_names = []
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=['195.148.125.135:9092'],
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id=None, consumer_timeout_ms=10000)
        sending_json = json.loads(data)
        sending_app_name = list(sending_json.keys())[0]
        for message in consumer:
            message = message.value
            stringify = json.loads(message)
            app_name = json.loads(stringify)
            for name in app_name:
                list_names.append(name)
        if sending_app_name not in list_names:
            producer = KafkaProducer(bootstrap_servers='195.148.125.135:9092',
                                     compression_type='gzip',
                                     max_request_size=3173440261,
                                     value_serializer=lambda x:
                                     dumps(x, ensure_ascii=False).encode('utf-8'))
            producer.send(topic, value=data)
            producer.flush()
