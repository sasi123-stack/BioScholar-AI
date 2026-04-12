import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.kafka_handler import get_kafka_handler
from src.utils.logger import logger

def test_handler_graceful_fail():
    print("Testing KafkaHandler graceful failure (when Kafka is down)...")
    handler = get_kafka_handler()
    
    # This should log an error but NOT crash the app
    result = handler.send_message("test_topic", {"message": "test"})
    
    if result is False:
        print("Success: Handler failed gracefully without crashing.")
    else:
        print("Unexpected: Handler reported success even though Kafka should be down.")

if __name__ == "__main__":
    test_handler_graceful_fail()
