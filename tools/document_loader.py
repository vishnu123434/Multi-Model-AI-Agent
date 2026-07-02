"""
tools/document_loader.py

Document Loader Tool

Supports:
1. PDF
2. DOCX
3. TXT

Loads document files, splits them into chunks,
and stores them in ChromaDB.
"""

import os
import shutil

from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


DB_PATH = "vectordb"


embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


def get_loader(file_path: str):

    extension = file_path.rsplit(".", 1)[1].lower()

    if extension == "pdf":
        return PyPDFLoader(file_path)

    elif extension == "docx":
        return Docx2txtLoader(file_path)

    elif extension == "txt":
        return TextLoader(file_path, encoding="utf-8")

    else:
        raise ValueError("Unsupported document type. Please upload PDF, DOCX, or TXT.")


def ingest_document(file_path: str):

    print("\nLoading Document...\n")

    loader = get_loader(file_path)

    documents = loader.load()

    print(f"Loaded {len(documents)} document sections.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = splitter.split_documents(documents)

    print(f"Created {len(chunks)} chunks.")

    if os.path.exists(DB_PATH):
        shutil.rmtree(DB_PATH)

    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory=DB_PATH
    )

    print("\nVector Database Created.\n")

    return vector_db