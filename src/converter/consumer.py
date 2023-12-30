import pika
import sys
import os
from pymongo import MongoClient
import gridfs
from convert import to_mp3
import logging

logging.basicConfig(level=logging.INFO)  # Set the desired logging level

def main():
    try:
        client = MongoClient('host.minikube.internal', 27017)
        db_videos = client.videos
        db_mp3s = client.mp3s

        fs_videos = gridfs.GridFS(db_mp3s)
        fs_mp3s = gridfs.GridFS(db_mp3s)

        connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        channel = connection.channel()

        def callback(ch, method, properties, body):
            try:
                err = to_mp3(body, fs_videos, fs_mp3s, ch)
                if err:
                    ch.basic_nack(delivery_tag=method.delivery_tag)
                else:
                    ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                logging.error(f"Error processing message: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag)

        channel.basic_consume(queue=os.environ.get("VIDEO_QUEUE"), on_message_callback=callback)

        logging.info("Waiting for messages...")

        channel.start_consuming()

    except KeyboardInterrupt:
        logging.info('Interrupted')
    finally:
        connection.close()  # Close RabbitMQ connection
        client.close()      # Close MongoDB client

if __name__ == "__main__":
    main()
