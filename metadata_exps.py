import os
import uuid
import arabic_reshaper
from bidi.algorithm import get_display

from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain_huggingface import HuggingFaceEmbeddings
from sentence_transformers import SentenceTransformer
from langchain.schema import Document
import random
from huggingface_hub import snapshot_download
import re
from collections import defaultdict


# Regex to match any ID: x, x-y, x-y-z, x-y-z-w
id_pattern = re.compile(r'^(\d+(?:-\d+){0,3})\b')

# A function to normalize IDs
def normalize_control_id(raw_id):
    # Arabic-Indic to Western numerals
    arabic_to_western = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
    normalized = raw_id.translate(arabic_to_western)
    
    # Replace separators to standard format
    normalized = normalized.replace('.', '-').replace(',', '-').strip()
    
    return normalized


def get_parent_id(control_id):
    out = []
    parts = control_id.split('-')
    if len(parts) > 1:
        out.append('-'.join(parts[:-1]))
    if len(parts) > 2:
        out.append('-'.join(parts[:-2]))
    return out  # top-level domain

def get_subcontrols(control_id):
    pattern = re.compile(rf'^{re.escape(control_id)}-\d+$')
    subcontrols = [cid for cid in all_ids if pattern.match(cid)]
    return subcontrols

def get_relevant_ids(id):
    ids = [id]
    ids.extend(get_parent_id(id))
    ids.extend(get_subcontrols(id))
    return ids

def get_all_descendants(control_id):
    # Count how many segments the parent has
    parent_parts = control_id.split('-')
    parent_depth = len(parent_parts)
    # Match any ID that starts with the control_id and has deeper hierarchy
    descendants = [
        cid for cid in all_ids
        if cid.startswith(control_id + '-') and len(cid.split('-')) > parent_depth
    ]
    return descendants

def chunk_by_control_units(text):
    lines = text.splitlines()
    chunks = []
    current_chunk = []
    current_id = None

    for line in lines:
        match = id_pattern.match(line.strip())
        if match:
            # Save the previous chunk before starting a new one
            if current_chunk and current_id:
                chunks.append({
                    "id": normalize_control_id(current_id),
                    "content": "\n".join(current_chunk).strip()
                })
            # Start a new chunk
            current_id = match.group(1)
            current_chunk = [line]
        else:
            current_chunk.append(line)
    
    # Add last chunk
    if current_chunk and current_id:
        chunks.append({
            "id": normalize_control_id(current_id),
            "content": "\n".join(current_chunk).strip()
        })

    return chunks



# 0) Make sure you’ve installed:
#    pip install arabic_reshaper python-bidi

# 1) Configuration
file_paths      = [r"C:\Users\mokar\KAUST Camp\project\OURPROJ\Guide to Essential Cybersecurity Controls Implementation.txt",
                   r"C:\Users\mokar\KAUST Camp\project\OURPROJ\Guide to Essential Cybersecurity Control - English.txt"]
# persist_path   = "./chroma_gemini_store"
persist_path   = "./chroma_e5_metadata_store"
google_api_key = "AIzaSyAMmd8GmGOFI7YyqB3iRLkWb2PJdGa3baA"

# reshaper for Arabic
reshaper = arabic_reshaper.ArabicReshaper()

# 2) Load & chunk the document
raw_docs = []

for file_path in file_paths:
    loader   = TextLoader(file_path, encoding="utf-8")
    raw_docs.extend(loader.load())

# print(f"type of raw docs: {type(raw_docs)}")
print("txt loaded successfully")

# splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
# docs     = splitter.split_documents(raw_docs)



docs = []
chunks = []

for doc in raw_docs:
    text = doc.page_content
    chunks.extend(chunk_by_control_units(text))
    
all_ids = set([c['id'] for c in chunks])

for chunk in chunks:
    control_id = normalize_control_id(chunk["id"])
    # control_id = chunk["id"]
    docs.append(Document(
        page_content=chunk["content"],
        metadata={
            "control_id": control_id,
            # "parent_id": get_parent_id(control_id),
            "relevant_ids": get_relevant_ids(control_id),
            "source": doc.metadata.get("source", "")
        }
    ))


# 3) (Optional) Print how many chunks you got
print(f"Total chunks: {len(chunks)}\n")
print(f"Total docs: {len(docs)}\n")
print(f"Total ids: {len(all_ids)}\n")
# print(f"Set ids: {len(set(all_ids))}\n")
print(f"\n\n{all_ids}\n\n")

print(f"\n\n\n")




# for i in range(10):
    # rand = random.randint(0, len(docs)-1) 
    # id = docs[rand].metadata['control_id']
    # ids = get_relevant_ids(id)
    # print(f"id: {id} \n relevant: {ids}\n\n")

    # id = docs[-rand].metadata['control_id']
    # ids = get_relevant_ids(id)
    # print(f"id: {id} \n relevant: {ids}\n\n")

    # reshaped_ans  = reshaper.reshape(docs[i].page_content)
    # display_answer = get_display(reshaped_ans)
    # print(display_answer)
    # print(docs[i].metadata)
    # print('\n\n')

    # print(docs[-i].metadata)
    # print('\n\n')



model_name = "intfloat/multilingual-e5-large"
model_kwargs = {'device': 'cpu'}
encode_kwargs = {'normalize_embeddings': False}
embed_model = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs,
)

# 5) Build & persist Chroma vectorstore
os.makedirs(persist_path, exist_ok=True)
ids = [str(uuid.uuid4()) for _ in docs]
# cannot use the control ids directly because they are duplicated (across ar & en, docs)

vectorstore = Chroma.from_documents(
    documents=docs,
    embedding=embed_model,
    persist_directory=persist_path,
    ids=ids,
)
vectorstore.persist()
print(f"✅ Chroma store persisted at {persist_path}")