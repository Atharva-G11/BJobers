from flask import Flask, request, jsonify
import fitz
from langchain_text_splitters import RecursiveCharacterTextSplitter
import requests
import weaviate
from weaviate.util import generate_uuid5
app = Flask(__name__)
file_path = "/Users/apple/Documents/Hackathon/data2.pdf"
model_id = "sentence-transformers/all-MiniLM-L6-v2"
hf_token = "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"
endpoint = "https://xgoacqulsnayhaevymofjw.c0.asia-southeast1.gcp.weaviate.cloud"
api_key = "NINlA1pO7yBV97iFZn7T7ul2feS00WnzluIq"
class_name = "Third_DB"
def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text
def chunk_text(text):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=100,
        chunk_overlap=20,
        length_function=len,
        is_separator_regex=False
    )
    return text_splitter.create_documents([text])
def embed_chunks(chunks):
    api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{model_id}"
    headers = {"Authorization": f"Bearer {hf_token}"}
    texts = [chunk.page_content for chunk in chunks]
    response = requests.post(api_url, headers=headers, json={"inputs": texts, "options": {"wait_for_model": True}})
    return response.json()
def setup_weaviate():
    return weaviate.Client(url=endpoint, auth_client_secret=weaviate.auth.AuthApiKey(api_key))
def create_schema(client):
    class_obj = {
        "class": class_name,
        "properties": [{"name": "Text", "dataType": ["text"]}]
    }
    client.schema.create_class(class_obj)
def load_to_weaviate(client, chunks, vectors):
    with client.batch(batch_size=200, num_workers=10) as batch:
        for i, vector in enumerate(vectors):
            vector_object = {"Text": chunks[i].page_content}
            batch.add_data_object(
                vector_object,
                class_name=class_name,
                vector=vector,
                uuid=generate_uuid5(vector_object)
            )
def query_weaviate(client, query_text):
    api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{model_id}"
    headers = {"Authorization": f"Bearer {hf_token}"}
    response = requests.post(api_url, headers=headers, json={"inputs": query_text})
    query_vector = response.json()[0]
    return client.query.get(class_name, ["Text"]).with_near_vector({"vector": query_vector}).with_limit(5).with_additional(['certainty']).do()
@app.route("/setup", methods=["POST"])
def setup_database():
    pdf_text = extract_text_from_pdf(file_path)
    chunks = chunk_text(pdf_text)
    vectors = embed_chunks(chunks)
    client = setup_weaviate()
    create_schema(client)
    load_to_weaviate(client, chunks, vectors)
    return jsonify({"message": "Database setup complete!"})
@app.route("/process_query", methods=["POST"])
def process_query():
    client = setup_weaviate()
    query_text = request.json.get("query")
    response = query_weaviate(client, query_text)
    return jsonify({"result": response})
if __name__ == "__main__":
    app.run(debug=True)