import pika

# Connect to RabbitMQ server
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Declare a scraper-queue
channel.queue_declare(queue='scraper-queue')

# Publish a message to the queue
channel.basic_publish(exchange='', routing_key='scraper-queue', body='Hello from scrapper-queue!')

print(" [x] Hello from scrapper-queue!")

# Close the connection
connection.close()