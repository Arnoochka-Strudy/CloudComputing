import pika
import json
import time
import random


class Producer:
    def __init__(self) -> None:
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host='rabbitmq',
                credentials=pika.PlainCredentials('user', 'password')
            )
        )
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='tasks', exchange_type='direct')

    def __call__(self, n: int = 10, k: int = 5) -> None:
        print("[Producer] Started")

        for _ in range(n):
            for _ in range(k):
                value = random.randint(1, 5)
                msg = {"value": value}

                self.channel.basic_publish(
                    exchange='tasks',
                    routing_key='calc',
                    body=json.dumps(msg)
                )
                print(f"[Producer] Sent: {msg}")

            time.sleep(3)


if __name__ == "__main__":
    producer = Producer()
    producer()
