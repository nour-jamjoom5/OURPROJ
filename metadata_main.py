# qa_chatbot.py

import os
import arabic_reshaper
from bidi.algorithm import get_display

from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.schema import BaseRetriever

from langchain.schema import BaseRetriever
from pydantic import Field
from typing import Any


class HybridRetriever(BaseRetriever):
    retriever: Any = Field()
    embedding_model: Any = Field()
    top_k: int = Field(default=10)

    def _get_relevant_documents(self, query: str):
        return hybrid_control_aware_retriever(query, self.retriever, self.embedding_model, top_k=self.top_k)

    async def _aget_relevant_documents(self, query: str):
        return self._get_relevant_documents(query)



# 1) Configuration
# The directory where the pre-built vector store is located.
persist_path = "./chroma_e5_metadata_store"
# Your Google API key for the LLM.
google_api_key = "AIzaSyCScdmSsl4tCM3vrMofoFv3BtOxJTZEjMI"

# A helper for reshaping Arabic text for correct display.
reshaper = arabic_reshaper.ArabicReshaper()


import re
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.schema.document import Document
from typing import List
import numpy as np

# def cosine_sim(a, b):
#     return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# def rerank_by_similarity(query_embedding, docs):
#     return sorted(docs, key=lambda doc: cosine_sim(query_embedding, doc.metadata['embedding']), reverse=True)

import re

def extract_control_ids(query: str):
    return re.findall(r'\b\d+(?:-\d+){0,3}\b', query)

def control_id_filter(user_query: str):
    control_ids = extract_control_ids(user_query)
    if not control_ids:
        return None  # no filter needed

    # Build regex string to match any of the relevant_ids
    regex_pattern = r"(" + "|".join(re.escape(cid) for cid in control_ids) + r")"
    return {"relevant_ids": {"$regex": regex_pattern}}


# A function to normalize IDs
def normalize_control_id(raw_id):
    # Arabic-Indic to Western numerals
    arabic_to_western = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
    normalized = raw_id.translate(arabic_to_western)
    
    # Replace separators to standard format
    normalized = normalized.replace('.', '-').replace(',', '-').strip()
    
    return normalized


def hybrid_control_aware_retriever(user_query, retriever, embedding_model, top_k=10):
    raw_ids = extract_control_ids(user_query)
    control_ids = [normalize_control_id(cid) for cid in raw_ids]

    for raw, norm in zip(raw_ids, control_ids):
        user_query = re.sub(rf'\b{re.escape(raw)}\b', norm, user_query)

    filter_dict = control_id_filter(user_query)


    if control_ids:
        # Filter by metadata first
        candidate_docs: List[Document] = retriever.similarity_search_with_score(
            query=user_query,
            k=50,  # Get more than top_k to rerank from
            filter=filter_dict
        )
        # Re-rank by score
        top_docs = sorted(candidate_docs, key=lambda x: x[1], reverse=True)[:top_k]
        return [doc for doc, score in top_docs]


    # No control IDs — fallback to semantic search
    return retriever.get_relevant_documents(user_query)


# 2) Load the pre-built Chroma vector store
print("Loading the Chroma vector store...")
# Define the embedding model used to create the store. It must be the same one.
model_name = "intfloat/multilingual-e5-large"
model_kwargs = {'device': 'cpu'}
encode_kwargs = {'normalize_embeddings': False}
embed_model = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs,
)

# Load the vector store from the specified directory.
vectorstore = Chroma(
    persist_directory=persist_path,
    embedding_function=embed_model,
)

print("✅ Chroma store loaded successfully!")

# 3) Set up Gemini LLM + RetrievalQA chain
# Initialize the Gemini LLM.
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    google_api_key=google_api_key
)

# Set up the RetrievalQA chain.
# It uses the vector store to retrieve relevant documents before generating an answer.

hybrid_retriever = HybridRetriever(
    retriever=vectorstore,
    embedding_model=embed_model,
    top_k=10
)

qa = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=hybrid_retriever,
    return_source_documents=True
)

# 4) Start the interactive Q&A session
print("\nYou can now ask questions (type 'exit' to end the session):\n")

while True:
    # Get user input.
    query = input("Your question: ").strip()

    if query.lower() in ["exit", "quit", "توقف"]:
        print("\nSession ended.")
        break

    try:
        # Run the query through the RetrievalQA chain.
        result = qa.invoke({"query": query})
        raw_answer = result["result"]
        # Reshape the answer for correct Arabic display.
        reshaped_ans = reshaper.reshape(raw_answer)
        display_answer = get_display(reshaped_ans)

        print("\nQuestion:")
        print(query)

        print("\nAnswer:")
        print(display_answer)

        # Print the source documents for context.
        print("\nRetrieved chunks:")
        for i, doc in enumerate(result["source_documents"], start=1):
            raw_chunk = doc.page_content
            reshaped_chunk = reshaper.reshape(raw_chunk)
            display_chunk = get_display(reshaped_chunk)

            print(f"[{i}] {display_chunk}\n")
    except Exception as e:
        print(f"An error occurred: {e}")
