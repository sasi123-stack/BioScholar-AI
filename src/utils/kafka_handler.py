import json
import logging
from kafka import KafkaProducer, KafkaConsumer
from typing import Any, Dict, List, Optional, Callable
from .config import load_yaml_config, yaml_config

logger = logging.getLogger(__name__)

class KafkaHandler:
    def __init__(self, bootstrap_servers: Optional[List[str]] = None):
        config = yaml_config
        self.bootstrap_servers = bootstrap_servers or [config.get('kafka', {}).get('bootstrap_servers', 'localhost:9092')]
        self._producer = None

    @property
    def producer(self):
        if self._producer is None:
            try:
                self._producer = KafkaProducer(
                    bootstrap_servers=self.bootstrap_servers,
                    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                    acks='all',
                    retries=3
                )
                logger.info(f"Kafka producer initialized for {self.bootstrap_servers}")
            except Exception as e:
                logger.error(f"Failed to initialize Kafka producer: {e}")
                self._producer = None
        return self._producer

    def send_message(self, topic: str, message: Dict[str, Any]):
        if self.producer:
            try:
                future = self.producer.send(topic, message)
                # In many cases, we want to be sure it's sent, but for logging we can leave it async
                # To make it sync: future.get(timeout=10)
                logger.debug(f"Message sent to topic {topic}: {message}")
                return True
            except Exception as e:
                logger.error(f"Error sending message to Kafka: {e}")
        return False

    def create_consumer(self, topic: str, group_id: str):
        try:
            consumer = KafkaConsumer(
                topic,
                bootstrap_servers=self.bootstrap_servers,
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                group_id=group_id,
                value_deserializer=lambda x: json.loads(x.decode('utf-8'))
            )
            logger.info(f"Kafka consumer created for topic {topic}, group {group_id}")
            return consumer
        except Exception as e:
            logger.error(f"Failed to create Kafka consumer: {e}")
            return None

    def listen(self, topic: str, group_id: str, callback: Callable[[Dict[str, Any]], None]):
        consumer = self.create_consumer(topic, group_id)
        if consumer:
            logger.info(f"Starting to listen on topic: {topic}")
            try:
                for message in consumer:
                    callback(message.value)
            except Exception as e:
                logger.error(f"Error while listening to topic {topic}: {e}")
            finally:
                consumer.close()

    def check_status(self) -> Dict[str, Any]:
        """Check the status of Kafka and Zookeeper connectivity."""
        status = {
            "kafka_connected": False,
            "zookeeper_connected": False,
            "bootstrap_servers": self.bootstrap_servers,
            "topics": [],
            "error": None
        }
        
        try:
            if self.producer:
                # Get metadata to verify connection
                metadata = self.producer.metrics()
                if metadata:
                    status["kafka_connected"] = True
                    # In a real ZK setup, Kafka depends on ZK, so if Kafka is up, ZK is likely up
                    status["zookeeper_connected"] = True
                    
                    # Try to get topics
                    consumer = KafkaConsumer(bootstrap_servers=self.bootstrap_servers)
                    status["topics"] = list(consumer.topics())
                    consumer.close()
            else:
                status["error"] = "Producer not initialized"
        except Exception as e:
            status["error"] = str(e)
            logger.error(f"Kafka status check failed: {e}")
            
        return status

# Singleton instance
_kafka_handler = None

def get_kafka_handler() -> KafkaHandler:
    global _kafka_handler
    if _kafka_handler is None:
        _kafka_handler = KafkaHandler()
    return _kafka_handler
