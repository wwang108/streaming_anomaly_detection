import logging
import os
from typing import List
from fastapi import FastAPI, HTTPException

from dotenv import load_dotenv
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka import SerializingProducer
from confluent_kafka.serialization import StringSerializer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer

from entities import TransactionModel
import schemas
from command import CreateTransactionCommand, CreatePredictCommand
import zlib
import uuid

import joblib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Load environment variables
load_dotenv(verbose=True)

# Load the machine learning model and scaler
model = joblib.load('isolation_forest_model.joblib')
scaler = joblib.load('scaler.joblib')


# Function for generating unique request IDs
def generate_request_id():
    # Generate a UUID and use a CRC32 hash to get a shorter integer
    return zlib.crc32(uuid.uuid4().bytes)

# Initialize FastAPI app
app = FastAPI()

# Kafka configuration setup
def get_kafka_config():
    # Load Kafka configuration from environment variables
    return {
        'bootstrap.servers': os.environ['BOOTSTRAP_SERVERS'],
        'security.protocol': os.environ['SECURITY_PROTOCOL'],
        'sasl.mechanisms': os.environ['SASL_MECHANISMS'],
        'sasl.username': os.environ['SASL_USERNAME'],
        'sasl.password': os.environ['SASL_PASSWORD'],
        # Additional configurations can be added here
    }

# FastAPI startup event to create Kafka topics
@app.on_event("startup")
async def startup_event():
    """
    Create Kafka topics on application startup using AdminClient and NewTopic.
    """
    admin_client = AdminClient(get_kafka_config())
    topic = [NewTopic(topic=os.getenv("TOPIC_NAME_ANOMALY"), num_partitions=3, replication_factor=3)]

    # Create topics and handle potential exceptions
    try:
        futures = admin_client.create_topics(topic)
        for topic_name, future in futures.items():
            future.result()
            logger.info(f"Create topic {topic_name}")
    except Exception as e:
        logger.warning(e)

# Function to create a Kafka producer with Avro serialization
def make_producer(schema_string: str) -> SerializingProducer:
    """
    Create and return a Kafka producer with Avro serialization.
    """
    schema_reg_client = SchemaRegistryClient({"url": os.getenv("schema_registry_url"),
                                              'basic.auth.user.info': os.environ['basic_auth.user_info']})
    value_serializer = AvroSerializer(schema_str=schema_string, 
                                      schema_registry_client=schema_reg_client,
                                      to_dict=lambda x, ctx: x.dict(by_alias=True))
    return SerializingProducer({
        **get_kafka_config(),
        "key.serializer": StringSerializer(),
        "value.serializer": value_serializer,
    })

# Callback class for Kafka producer to handle message delivery reports
class ProducerCallback:
    """
    Callback class for Kafka producer to handle message delivery reports.
    """
    def __call__(self, err, msg):
        if err is not None:
            logger.error(f"Delivery failed for record: {err}")
        else:
            logger.info(f"Record delivered to {msg.topic()}")

# FastAPI endpoint for generating a transaction
@app.post("/api/send-transaction")
async def generate_trip(command: CreateTransactionCommand):
    """
    Endpoint to generate a transaction.
    """

    request_id = generate_request_id()
    producer = make_producer(schemas.transaction_schema)

    # Produce and send the transaction to Kafka topic
    producer.produce(topic=os.environ['TOPIC_NAME_ANOMALY'],
                     key=str(request_id),
                     value=TransactionModel(**command.dict()),
                     on_delivery=ProducerCallback())
    producer.flush()
    return command

# FastAPI endpoint for making a prediction

@app.post("/api/predict")
async def predict(input_data: CreatePredictCommand):
    # Endpoint for model prediction
    try:
        data = [[input_data.size, input_data.virtual_size, input_data.input_count, 
                 input_data.output_count, input_data.input_value,
                 input_data.output_value, input_data.fee]]
        result = model.predict(scaler.transform(data))[0]
        return str(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
