import json
from kafka import KafkaConsumer

hostname = '10.148.0.8'
port = '9092'
topic_name = 'forex'

# Create a KafkaConsumer with ASCII deserialization
consumer = KafkaConsumer(
    topic_name,
    bootstrap_servers=f'{hostname}:{port}',
    value_deserializer=lambda v: json.loads(v.decode('ascii'))
)

# Continuously consume messages
for message in consumer:
    value = message.value  # Deserialized message value
    print(value)
    # Process the deserialized message as needed
    # ...

# Close the consumer when finished
consumer.close()
