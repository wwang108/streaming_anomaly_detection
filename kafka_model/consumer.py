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
import schemas,requests, json
from entities import TransactionModel
import time
from datetime import datetime
from mongo_action import MongoDBCollection
from dotenv import load_dotenv
import os

load_dotenv(verbose=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

executor = concurrent.futures.ThreadPoolExecutor(max_workers=3)

predict_url = 'http://localhost:8001/api/predict'
data_store = []

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

load_dotenv(verbose=True)
def make_consumer(entityModel, schema_str, group_id) -> DeserializingConsumer:
    schema_registry_url = os.environ['schema_registry_url']
    basic_auth_user_info = os.environ.get('basic_auth.user_info')  # Make sure this environment variable is set in your .env file

    schema_reg_config = {
        'url': schema_registry_url,
        'basic.auth.user.info': basic_auth_user_info
    }
    schema_reg_client = SchemaRegistryClient(schema_reg_config)

    avro_deserializer = AvroDeserializer(
        schema_str=schema_str,
        schema_registry_client=schema_reg_client,
        from_dict=lambda data, ctx: entityModel(**data)
    )

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

async def consume(topic_name, entityModel, schema_str, group_id):
    logger.info(f"Started Python Avro Consumer for topic {topic_name}")


    consumer = make_consumer(entityModel, schema_str, group_id)
    consumer.subscribe([topic_name])

    try:
        loop = asyncio.get_running_loop()
        while True:
            msg = await loop.run_in_executor(executor, consumer.poll, 1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition event
                    logger.info('End of partition reached {0}/{1}'
                                .format(msg.topic(), msg.partition()))
                else:
                    logger.error(msg.error())
                continue

            input_data = msg.value()
            if input_data is not None:
                data = {'size':input_data.size, 
                        'virtual_size':input_data.virtual_size, 
                        'input_count':input_data.input_count, 
                        'output_count':input_data.output_count,
                        'input_value':input_data.input_value,
                        'output_value':input_data.output_value, 
                        'fee':input_data.fee}
                try:
                    response = requests.post(predict_url, data=json.dumps(data), headers={'Content-Type': 'application/json'})
                    data_store.append(response.json())
                    print(response.status_code)
                    print(response.json()) 
                    input_data = input_data.dict()
                    input_data['writein_time'] = datetime.now()
                    print("==================", input_data)
                    if response.json() == '1':
                        try:
                            
                            normal_clinet.insert_transaction(input_data)
                        except:
                            print("store fails")
                    else:
                        try:
                            anormal_client.insert_transaction(input_data)
                        except:
                            print("store fails")
                except:
                    logger.info("Cannot get prediction")
                # logger.info(f"Consumed {topic_name}: {input_data}")
                consumer.commit(message=msg)  # Manually commit the message
    except KeyboardInterrupt:
        logger.info("Consumer interrupted by the user.")
    finally:
        # Close down consumer to commit final offsets.
        consumer.close()
        logger.info("Consumer closed.")
async def consume_together():
    await asyncio.gather(
        consume(os.environ['TOPIC_NAME_ANOMALY'], TransactionModel, schemas.transaction_schema, os.environ['CONSUMER_GROUP_ID_ANOMALY_0']),
        # consume(os.environ['TOPIC_NAME_ANOMALY'], TransactionModel, schemas.transaction_schema, os.environ['CONSUMER_GROUP_ID_ANOMALY_1']),
        # consume(os.environ['TOPIC_NAME_ANOMALY'], TransactionModel, schemas.transaction_schema, os.environ['CONSUMER_GROUP_ID_ANOMALY_2'])
    )
def main():

    try:
        asyncio.run(consume_together())
    except KeyboardInterrupt as e:
        print("stop!")

if __name__ == '__main__':
    main()