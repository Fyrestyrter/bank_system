import json
import time
from kafka import KafkaConsumer, KafkaProducer

time.sleep(15)
consumer = KafkaConsumer('raw_docs', bootstrap_servers=['kafka:9092'],
                         value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                         group_id='gwfi_group')
producer = KafkaProducer(bootstrap_servers=['kafka:9092'],
                         value_serializer=lambda x: json.dumps(x).encode('utf-8'))

for message in consumer:
    doc = message.value

    print(json.dumps({
        "timestamp": time.time(),
        "service": "gwfi",
        "event": "doc_received",
        "doc_id": doc.get('doc_id'),
        "level": "info"
    }), flush=True)

    payload_content = str(doc.get('payload', ''))
    if "SELECT" in payload_content or "DROP" in payload_content:
        print(json.dumps({
            "timestamp": time.time(),
            "service": "gwfi",
            "event": "security_alert",
            "reason": "sql_injection",
            "client_id": doc.get('client_id'),
            "payload": payload_content,
            "level": "error"
        }), flush=True)
        continue

    if not doc.get('cert_valid'):
        print(json.dumps({
            "timestamp": time.time(),
            "service": "gwfi",
            "event": "security_alert",
            "reason": "invalid_cert",
            "client_id": doc.get('client_id'),
            "payload": "Certificate check failed",
            "level": "error"
        }), flush=True)
        continue

    producer.send('validated_docs', value=doc)