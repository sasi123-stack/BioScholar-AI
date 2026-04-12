import sys
import os
import time

# Add the project root to sys.path to allow imports from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.kafka_handler import get_kafka_handler
from src.utils.config import get_config
from src.utils.logger import logger

def process_search_log(message):
    try:
        msg_type = message.get("type", "unknown")
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(message.get("timestamp", time.time())))
        
        if msg_type == "search":
            query = message.get("query", "")
            index = message.get("index", "")
            print(f"🔍 [KAFKA LOG] {timestamp} | SEARCH | Query: '{query}' | Index: {index}")
        elif msg_type == "question":
            question = message.get("question", "")
            index = message.get("index", "")
            print(f"❓ [KAFKA LOG] {timestamp} | QUESTION | Text: '{question}' | Index: {index}")
        else:
            print(f"📦 [KAFKA LOG] {timestamp} | OTHER | {message}")
            
    except Exception as e:
        logger.error(f"Error processing Kafka message: {e}")

def main():
    config = get_config()
    kafka_handler = get_kafka_handler()
    
    topic = config.get('kafka', {}).get('topics', {}).get('search_logs', 'search_logs')
    group_id = config.get('kafka', {}).get('group_ids', {}).get('search_logger', 'search_logger_group')
    
    print(f"🚀 Starting Kafka Search Logger Consumer...")
    print(f"📡 Listening on topic: {topic}")
    print(f"👥 Group ID: {group_id}")
    print("-" * 50)
    
    try:
        kafka_handler.listen(topic, group_id, process_search_log)
    except KeyboardInterrupt:
        print("\n👋 Consumer stopped by user.")
    except Exception as e:
        print(f"❌ Consumer failed: {e}")

if __name__ == "__main__":
    main()
