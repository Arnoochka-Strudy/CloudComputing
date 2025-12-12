import pika
import json


class Consumer:
    def __init__(self) -> None:
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host='rabbitmq',
                credentials=pika.PlainCredentials('user', 'password')
            )
        )
        self.channel = self.connection.channel()

        self.channel.exchange_declare(exchange='tasks', exchange_type='direct')
        self.channel.exchange_declare(exchange='dlx', exchange_type='direct')
        self.channel.queue_declare(
            queue='main-queue',
            durable=True,
            arguments={
                "x-dead-letter-exchange": "dlx",
                "x-dead-letter-routing-key": "dlq"
            }
        )

        self.channel.queue_declare(queue='dlq', durable=True)
        self.channel.queue_bind(
            exchange='dlx',
            queue='dlq',
            routing_key='dlq'
        )

        self.channel.queue_bind(
            exchange='tasks',
            queue='main-queue',
            routing_key='calc'
        )

    def __call__(self) -> None:
        print("[Consumer] Started. Waiting for messages...")
        self.channel.basic_consume(
            queue='main-queue',
            on_message_callback=self.callback
        )
        self.channel.start_consuming()

    def process_message(self, value: int):
        if value % 5 == 0:
            raise ValueError("Bad number — failing intentionally")
        return value * 2

    def callback(self, ch, method, properties, body):
        msg = json.loads(body)
        value = msg.get("value")

        try:
            result = self.process_message(value)
            print(f"[Consumer] Success: {value} → {result}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print(f"[Consumer] ERROR processing {value}: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


if __name__ == "__main__":
    consumer = Consumer()
    consumer()
