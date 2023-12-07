import logging
import os
import asyncio
from dotenv import load_dotenv
from confluent_kafka import DeserializingConsumer
from confluent_kafka.error import KafkaError
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import StringDeserializer
import concurrent.futures
import schemas, requests, json
from entities import TransactionModel
import time
from datetime import datetime
from mongo_action import MongoDBCollection

# Load environment variables from .env file
load_dotenv(verbose=True)

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Executor for running asynchronous tasks
executor = concurrent.futures.ThreadPoolExecutor(max_workers=3)

# URL for the prediction API
predict_url = 'http://localhost:8001/api/predict'
data_store = []

# MongoDB clients for normal and anomalous transactions
normal_clinet  = MongoDBCollection(os.environ.get("MONGO_USERNAME"),
                                   os.environ.get("MONGO_PASSWORD"),
                                   os.environ.get("MONGO_IP"),
                                   os.environ.get("MONGO_DB_NAME_NORMAL"),
                                   os.environ.get("MONGO_COLLECTION_NAME_NORMAL"))

anormal_client = MongoDBCollection(os.environ.get("MONGO_USERNAME"),
                                   os.environ.get("MONGO_PASSWORD"),
                                   os.environ.get("MONGO_IP"),
                                   os.environ.get("MONGO_DB_NAME_ANORMAL"),
                                   os.environ.get("MONGO_COLLECTION_NAME_ANORMAL"))

# Function to create a Kafka consumer
def make_consumer(entityModel, schema_str, group_id) -> DeserializingConsumer:
    # Load environment variables for Kafka and Schema Registry
    schema_registry_url = os.environ['schema_registry_url']
    basic_auth_user_info = os.environ.get('basic_auth.user_info')

    # Configure Schema Registry client
    schema_reg_config = {
        'url': schema_registry_url,
        'basic.auth.user.info': basic_auth_user_info
    }
    schema_reg_client = SchemaRegistryClient(schema_reg_config)

    # Set up Avro deserializer with the schema
    avro_deserializer = AvroDeserializer(
        schema_str=schema_str,
        schema_registry_client=schema_reg_client,
        from_dict=lambda data, ctx: entityModel(**data)
    )

    # Kafka consumer configuration
    consumer_config = {
        'bootstrap.servers': os.environ['BOOTSTRAP_SERVERS'],
        'security.protocol': os.environ['SECURITY_PROTOCOL'],
        'sasl.mechanisms': os.environ['SASL_MECHANISMS'],
        'sasl.username': os.environ['SASL_USERNAME'],
        'sasl.password': os.environ['SASL_PASSWORD'],
        'key.deserializer': StringDeserializer('utf_8'),
        'value.deserializer': avro_deserializer,
        'group.id': group_id,
        'auto.offset.reset': 'latest',
        'enable.auto.commit': 'false'  # Changed to false to manually commit offsets
    }

    return DeserializingConsumer(consumer_config)

# Asynchronous function to consume messages from a Kafka topic
async def consume(topic_name, entityModel, schema_str, group_id):
    logger.info(f"Started Python Avro Consumer for topic {topic_name}")

    consumer = make_consumer(entityModel, schema_str, group_id)
    consumer.subscribe([topic_name])

    try:
        loop = asyncio.get_running_loop()
        while True:
            # Poll messages from Kafka
            msg = await loop.run_in_executor(executor, consumer.poll, 1.0)
            # Handle message processing
            # [Message processing logic goes here...]

            # Commit the message after processing
            consumer.commit(message=msg)  # Manually commit the message
    except KeyboardInterrupt:
        logger.info("Consumer interrupted by the user.")
    finally:
        # Close down consumer to commit final offsets.
        consumer.close()
        logger.info("Consumer closed.")

# Asynchronous function to consume from multiple topics simultaneously
async def consume_together():
    await asyncio.gather(
        consume(os.environ['TOPIC_NAME_ANOMALY'], TransactionModel, schemas.transaction_schema, os.environ['CONSUMER_GROUP_ID_ANOMALY_0']),
        # Additional consumers can be added here
    )

# Main function
def main():
    try:
        asyncio.run(consume_together())
    except KeyboardInterrupt as e:
        print("stop!")

if __name__ == '__main__':
    main()
