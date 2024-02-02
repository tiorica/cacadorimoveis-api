import pika

# Connect to RabbitMQ server
def message_broker_send_message(message_body):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    # Declare a scraper-queue
    channel.queue_declare(queue='scraper-queue')
    # Publish a message to the queue
    channel.basic_publish(exchange='', routing_key='scraper-queue', body=message_body)

    # Close the connection
    connection.close()