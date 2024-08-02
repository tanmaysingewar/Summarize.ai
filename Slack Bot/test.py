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
        chunk_size=2000,
        length_function=len,
        is_separator_regex=False,
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


channel_id = "channel_123"
file_id = "file_abc"

# Add documents to the store
text = """
The Eiffel Tower is located in Paris. The Great Wall of China is one of the seven wonders of the world.
The Mona Lisa is a famous painting by Leonardo da Vinci. The Pyramids of Giza are ancient pyramid structures in Egypt.
The Statue of Liberty is a famous landmark in New York City.
"""
add_document(channel_id, file_id, text)

# Query the document store
question = "Where is the Eiffel Tower located?"
results = query(channel_id, question)

# Print the results
for result in results:
    print(result)

print("\n\n ========== \n\n")

channel_id = "channel_123"
file_id = "file_abcd"

# Add documents to the store
text = """
India, officially the Republic of India (ISO: Bhārat Gaṇarājya),[21] is a country in South Asia. It is the seventh-largest country by area; the most populous country as of June 2023;[22][23] and from the time of its independence in 1947, the world's most populous democracy.[24][25][26] Bounded by the Indian Ocean on the south, the Arabian Sea on the southwest, and the Bay of Bengal on the southeast, it shares land borders with Pakistan to the west;[j] China, Nepal, and Bhutan to the north; and Bangladesh and Myanmar to the east. In the Indian Ocean, India is in the vicinity of Sri Lanka and the Maldives; its Andaman and Nicobar Islands share a maritime border with Thailand, Myanmar, and Indonesia.
"""
add_document(channel_id, file_id, text)

# Query the document store
question = "Where is the Eiffel Tower"
results = query(channel_id, question)

# Print the results
for result in results:
    print(result)