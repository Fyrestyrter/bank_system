import json
import time
import random
from kafka import KafkaConsumer

time.sleep(20)
consumer = KafkaConsumer('validated_docs', bootstrap_servers=['kafka:9092'],
                         value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                         group_id='adapter_group')

for message in consumer:
    doc = message.value

    delay = doc.get('db_delay', 0.05)
    time.sleep(delay)

    print(json.dumps({
        "timestamp": time.time(),
        "service": "adapter",
        "event": "processed",
        "doc_id": doc.get('doc_id'),
        "doc_type": doc.get('doc_type'),
        "client_id": doc.get('client_id'),
        "amount": doc.get('amount'),
        "currency": doc.get('currency'),
        "shard_id": doc.get('shard_id'),
        "processing_time": delay,
        "factory": random.choice(["FACTORY_MOSCOW", "FACTORY_SPB", "FACTORY_NSK"])
    }), flush=True)