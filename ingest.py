import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

def start_ingestion(pdf_path="support_policy.pdf", vector_db_path="./chroma_db"):
    if not os.path.exists(pdf_path):
        print(f"Error: {pdf_path} not found. Did you run mock_data.py?")
        return

    print("Loading PDF document...")
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()

    print("Chunking document...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=150
    )
    splits = text_splitter.split_documents(docs)

    print(f"Created {len(splits)} chunks.")
    
    print("Initializing local HuggingFace embedding model...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    print("Building local Vector Store with Chroma...")
    # Initialize Chroma, inserting documents
    vectorstore = Chroma.from_documents(
        documents=splits, 
        embedding=embeddings, 
        persist_directory=vector_db_path
    )
    
    print(f"Ingestion complete. Vector store saved to {vector_db_path}")

if __name__ == "__main__":
    start_ingestion()
