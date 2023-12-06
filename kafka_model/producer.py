
# Standard library imports for logging, operating system interactions, and type annotations
import logging
import os
from typing import List
# FastAPI framework for building APIs and handling HTTP requests and responses
from fastapi import FastAPI, HTTPException, status

# dotenv for loading environment variables from a .env file for configuration
from dotenv import load_dotenv

# Confluent Kafka client libraries for producing messages and managing Kafka topics
from confluent_kafka.admin import AdminClient, NewTopic  # Kafka administration (topics management)
from confluent_kafka import SerializingProducer  # Kafka producer with serialization capabilities
from confluent_kafka.serialization import StringSerializer  # Serializer for message keys
from confluent_kafka.schema_registry import SchemaRegistryClient  # For schema registry interactions
from confluent_kafka.schema_registry.avro import AvroSerializer  # Avro serializer for message values

# Local modules containing application-specific classes and schemas

from entities import TransactionModel, InputModel, OutputModel
import schemas
from command import CreateTransactionCommand,CreatePredictCommand
# # Libraries for compressing data, and creating unique identifiers
import zlib  # Compression library for generating shorter unique IDs using CRC32
import uuid  # Library for generating unique identifiers

#############################
import joblib

## Read parquet data


## Convert each row parquet data into a Transaction model

# def create_transaction_model(row_dict):
#     # Process the nested 'inputs' and 'outputs'
#     if row_dict['inputs'] != None:
#         inputs = [InputModel(**input_data) for input_data in row_dict['inputs']]
#     else:
#         inputs = None
#     if row_dict['outputs'] != None:
#         outputs = [OutputModel(**output_data) for output_data in row_dict['outputs']]
#     else:
#         outputs = None
#     # Create a TransactionModel, passing in the processed inputs and outputs
#     transaction = TransactionModel(
#         date=row_dict.get('date'),
#         hash=row_dict.get('hash'),
#         size=row_dict.get('size'),
#         virtual_size=row_dict.get('virtual_size'),
#         version=row_dict.get('version'),
#         lock_time=row_dict.get('lock_time'),
#         block_hash=row_dict.get('block_hash'),
#         block_number=row_dict.get('block_number'),
#         block_timestamp=row_dict['block_timestamp'].isoformat() if pd.notnull(row_dict['block_timestamp']) else None,
#         index=row_dict.get('index'),
#         input_count=row_dict.get('input_count'),
#         output_count=row_dict.get('output_count'),
#         input_value=row_dict.get('input_value'),
#         output_value=row_dict.get('output_value'),
#         is_coinbase=row_dict.get('is_coinbase'),
#         fee=row_dict.get('fee'),
#         inputs=inputs if inputs else None,
#         outputs=outputs if outputs else None
#     )
#     return transaction


def generate_request_id():
    # Generate a UUID and use a CRC32 hash to get a shorter integer
    return zlib.crc32(uuid.uuid4().bytes)

# standard module for logging messages
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# loading secrets to connect confluent kafka
load_dotenv(verbose=True)


app = FastAPI()

model = joblib.load('isolation_forest_model.joblib')
scaler = joblib.load('scaler.joblib')

# 1. Kafka Configuration
def get_kafka_config():
    """
    Load Kafka configuration from environment variables.
    HINT: Use os.getenv to load environment variables for Kafka configuration.
    """
    return {
        'bootstrap.servers': os.environ['BOOTSTRAP_SERVERS'],
        'security.protocol': os.environ['SECURITY_PROTOCOL'],
        'sasl.mechanisms': os.environ['SASL_MECHANISMS'],
        'sasl.username': os.environ['SASL_USERNAME'],
        'sasl.password': os.environ['SASL_PASSWORD'],
        # TODO: Add other configurations here (e.g., security settings)
    }

# 2. Create the Topic if doesn't exist 

@app.on_event("startup")
async def startup_event():
    """
    Create Kafka topics on application startup.
    HINT: Use AdminClient and NewTopic to create Kafka topics.
    """
    admin_client = AdminClient(get_kafka_config())
    topic = [NewTopic(topic=os.getenv("TOPIC_NAME_ANOMALY"), num_partitions=3, replication_factor=3)]

    # TODO: Create topics (handle potential exceptions)
    try:
        futures = admin_client.create_topics(topic)
        for topic_name, future in futures.items():
            future.result()
            logger.info(f"Create topic {topic_name}")
    except Exception as e:
        logger.warning(e)

# 3. Kafka Producer Setup
def make_producer(schema_string: str) -> SerializingProducer:
    """
    Create and return a Kafka producer with Avro serialization.
    HINT: Use AvroSerializer for value_serializer.
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

# 4. Producer Callback
class ProducerCallback:
    """
    Callback class for Kafka producer to handle message delivery reports.
    """
    def __call__(self, err, msg):
        if err is not None:
            logger.error(f"Delivery failed for record: {err}")
        else:
            logger.info(f"Record delivered to {msg.topic()}")

# 5. FastAPI Endpoints Implementation
@app.post("/api/send-transaction")
async def generate_trip(command: CreateTransactionCommand):
    """
    Endpoint to generate a transaction.
    """

    request_id = generate_request_id()
    producer = make_producer(schemas.transaction_schema)

    producer.produce(topic=os.environ['TOPIC_NAME_ANOMALY'],
                     key=str(request_id),
                     value=TransactionModel(**command.dict()),
                     on_delivery=ProducerCallback())
    producer.flush()
    return command

@app.post("/api/predict")
async def predict(input_data: CreatePredictCommand):
    try:
        # Replace this with your actual model prediction logic
        data = [[input_data.size, input_data.virtual_size, input_data.input_count, 
                 input_data.output_count,input_data.input_value,
                 input_data.output_value, input_data.fee]]
        result = model.predict(scaler.transform(data))[0]
        prediction = f"Model prediction for {result} "
        return str(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))