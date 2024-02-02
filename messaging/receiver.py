import pika

# Connect to RabbitMQ server
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Declare the queue
channel.queue_declare(queue='hello')

# Callback function to process incoming messages
def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)

# Subscribe to the queue and consume messages
channel.basic_consume(queue='hello', on_message_callback=callback, auto_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')

# Start consuming messages
channel.start_consuming()
