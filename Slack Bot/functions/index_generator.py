import os
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from langchain_text_splitters import RecursiveCharacterTextSplitter

def get_channel_dir(channel_id):
    return os.path.join("index", channel_id)

def get_file_paths(channel_id, file_id):
    channel_dir = get_channel_dir(channel_id)
    os.makedirs(channel_dir, exist_ok=True)  # Ensure directory exists
    index_file = os.path.join(channel_dir, f"{file_id}_index.pkl")
    vectorizer_file = os.path.join(channel_dir, f"{file_id}_vectorizer.pkl")
    return index_file, vectorizer_file

def clear_old_files(channel_id, current_file_id):
    channel_dir = get_channel_dir(channel_id)
    if not os.path.exists(channel_dir):
        return
    for filename in os.listdir(channel_dir):
        if filename.endswith("_index.pkl") or filename.endswith("_vectorizer.pkl"):
            file_id = filename.split('_')[0]
            if file_id != current_file_id:
                os.remove(os.path.join(channel_dir, filename))

def load_index(channel_id):
    global documents, document_matrix, vectorizer
    channel_dir = get_channel_dir(channel_id)
    
    index_file, vectorizer_file = None, None

    if os.path.exists(channel_dir):
        for filename in os.listdir(channel_dir):
            if filename.endswith("_index.pkl"):
                index_file = os.path.join(channel_dir, filename)
            elif filename.endswith("_vectorizer.pkl"):
                vectorizer_file = os.path.join(channel_dir, filename)

    if index_file and vectorizer_file:
        documents = joblib.load(index_file)
        vectorizer = joblib.load(vectorizer_file)
        document_matrix = vectorizer.transform(documents)
    else:
        documents = []
        vectorizer = TfidfVectorizer()
        document_matrix = None

def save_index(channel_id, file_id):
    index_file, vectorizer_file = get_file_paths(channel_id, file_id)
    joblib.dump(documents, index_file)
    joblib.dump(vectorizer, vectorizer_file)

def add_document(channel_id, file_id, text):
    global documents, document_matrix, vectorizer
    clear_old_files(channel_id, file_id)
    
    load_index(channel_id)
    
    # Split the text into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,
        length_function=len,
        is_separator_regex=False,
        chunk_overlap=20,
    )
    chunks = text_splitter.create_documents([text])
    
    # Extract text from Document objects using the 'page_content' attribute
    chunk_texts = [chunk.page_content for chunk in chunks]

    documents.extend(chunk_texts)
    vectorizer = TfidfVectorizer()
    document_matrix = vectorizer.fit_transform(documents)
    save_index(channel_id, file_id)

def query(channel_id, user_prompt, top_k=5):
    load_index(channel_id)
    if not documents:
        return []
    query_vector = vectorizer.transform([user_prompt])
    similarities = cosine_similarity(query_vector, document_matrix).flatten()
    indices = similarities.argsort()[-top_k:][::-1]
    return [documents[i] for i in indices]

__all__ = ["add_document", "query"]