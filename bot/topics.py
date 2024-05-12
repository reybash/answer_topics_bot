import json
from dataclasses import dataclass


@dataclass
class Topic:
    name_topic: str
    data_topic: str
    file_name: str

    topics = []

    def __post_init__(self):
        Topic.topics.append(self)


def load_topics_from_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        topics_data = json.load(file)
    return [Topic(data["name_topic"], data["data_topic"],
                  "questions/" + data["file_name"]) for data in topics_data]


topics = load_topics_from_json('./topics.json')
