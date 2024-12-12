import weaviate
from weaviate.util import generate_uuid5
client = weaviate.Client(
    url="https://your-weaviate-instance.com",
    auth_client_secret=weaviate.auth.AuthApiKey(api_key="NINlA1pO7yBV97iFZn7T7ul2feS00WnzluIq")
)
class_obj = {
    "class": "Third_DB",
    "properties": [
        {"name": "Text", "dataType": ["text"]}
    ]
}
client.schema.create_class(class_obj)
with open('../data/extracted_text.txt', 'r') as f:
    text_data = f.readlines()
with client.batch(batch_size=200) as batch:
    for text in text_data:
        data_object = {"Text": text}
        batch.add_data_object(
            data_object,
            class_name="Third_DB",
            uuid=generate_uuid5(data_object)
        )