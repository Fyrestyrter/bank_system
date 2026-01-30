import time
import json
import random
import threading
import uuid
from kafka import KafkaProducer
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

CLIENTS = [f"CORP_INN_{random.randint(7700000000, 7799999999)}" for _ in range(200)]
DOC_TYPES = {
    "PAYMENT_ORDER": {"code": "103", "weight": 70},
    "STATEMENT_REQ": {"code": "940", "weight": 15},
    "FX_ORDER": {"code": "MT202", "weight": 10},
    "CREDIT_APP": {"code": "APP_01", "weight": 5}
}
CURRENCIES = ["RUB", "RUB", "RUB", "USD", "EUR", "CNY"]

app_state = {
    "mode": "normal",
    "lag_shard": None,
    "intensity": 0.5
}

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.post("/set_mode/{mode}")
def set_mode(mode: str):
    app_state["mode"] = mode
    app_state["intensity"] = 0.05 if mode == "overload" else 0.5
    return {"status": mode}


@app.post("/set_lag/{shard_id}")
def set_lag(shard_id: int):
    app_state["lag_shard"] = shard_id
    return {"status": f"lag_on_{shard_id}"}


@app.post("/reset")
def reset():
    app_state["mode"] = "normal"
    app_state["lag_shard"] = None
    app_state["intensity"] = 0.5
    return {"status": "reset"}


def get_realistic_amount():
    chance = random.random()
    if chance < 0.01:
        return round(random.uniform(50_000_000, 500_000_000), 2)
    elif chance < 0.10:
        return round(random.uniform(500_000, 5_000_000), 2)
    else:
        return round(random.uniform(1_000, 100_000), 2)


def data_loop():
    producer = KafkaProducer(
        bootstrap_servers=['kafka:9092'],
        value_serializer=lambda x: json.dumps(x).encode('utf-8')
    )

    while True:
        d_type = random.choices(list(DOC_TYPES.keys()), weights=[v['weight'] for v in DOC_TYPES.values()])[0]

        is_attack = (app_state["mode"] == "attack" and random.random() < 0.3)
        cert_valid = False if is_attack and random.random() < 0.5 else True
        payload = "SELECT * FROM secrets" if is_attack else f"Ref: {uuid.uuid4().hex[:8]}"

        shard_id = random.randint(1, 4)
        db_delay = 1.2 if str(shard_id) == str(app_state["lag_shard"]) else 0.05

        doc = {
            "service": "generator",
            "event": "new_document",
            "doc_id": str(uuid.uuid4()),
            "doc_type": d_type,
            "doc_code": DOC_TYPES[d_type]["code"],
            "client_id": random.choice(CLIENTS),
            "amount": get_realistic_amount(),
            "currency": random.choice(CURRENCIES),
            "shard_id": shard_id,
            "cert_valid": cert_valid,
            "payload": payload,
            "db_delay": db_delay,
            "timestamp": time.time()
        }

        producer.send('raw_docs', value=doc)
        print(json.dumps(doc), flush=True)
        time.sleep(app_state["intensity"])


threading.Thread(target=data_loop, daemon=True).start()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)