import os, json, time
from dotenv import load_dotenv # type: ignore
from elasticsearch import Elasticsearch, helpers # type: ignore

INDEX_NAME = "main_index"

load_dotenv(dotenv_path="elastic-start-local/.env")
ES_URL = os.getenv("ES_LOCAL_URL")
PASSWD = os.getenv("ES_LOCAL_PASSWORD")
USR = "elastic"

MAPPING = {
    "settings": {
        "analysis": {
            "filter": {
                "english_stop": {"type": "stop", "stopwords": "_english_"},
                "english_stemmer": {"type": "stemmer", "language": "english"},
                "english_possessive_stemmer": {"type": "stemmer", "language": "possessive_english"},
            },
            "analyzer": {
                "standard_custom": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": [
                        "english_possessive_stemmer",
                        "lowercase",        # necessario, solo il tokenizer è standard
                        "asciifolding",
                        "english_stop",
                        "english_stemmer",
                    ],
                }
            },
        }
    },
    "mappings": {
        "properties": {
            "title": {
                "type": "text",
                "analyzer": "standard",
                "search_analyzer": "standard",
            },
            "content": {
                "type": "text",
                "analyzer": "standard_custom",
                "search_analyzer": "standard_custom",
            },
        }
    },
}

JSON_FOLDER = "to_index_dataset"

def build_index():    
    es = Elasticsearch(ES_URL, basic_auth=(USR,PASSWD))
    
    index_name = "main_index"
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)
    es.indices.create(index=index_name, body=MAPPING)
    print(f"Index '{index_name}' successfully created.")

    actions = []
    for file in os.listdir(JSON_FOLDER):
        path = os.path.join(JSON_FOLDER, file)
        with open(path, "r", encoding="utf-8") as f:
            json_file = json.load(f)
        action = {
            "_index": index_name,
            "_source": {
                "title": json_file["title"],
                "content": json_file["content"]
            }
        }
        actions.append(action)

    start = time.perf_counter()
    success, _ = helpers.bulk(es, actions, request_timeout=120)
    elapsed = time.perf_counter() - start
    print(f"Documents successfully indexed: {success}")
    return elapsed
    
if __name__ == "__main__":
    build_index()