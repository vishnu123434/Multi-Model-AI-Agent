"""
tools/document_loader.py

Loads PDF/DOCX/TXT documents, splits them,
and stores them in a fresh ChromaDB folder per upload.
"""

import os
import uuid

from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


BASE_DB_PATH = "vectordb"

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


def get_loader(file_path: str):
    extension = file_path.rsplit(".", 1)[1].lower()

    if extension == "pdf":
        return PyPDFLoader(file_path)

    if extension == "docx":
        return Docx2txtLoader(file_path)

    if extension == "txt":
        return TextLoader(file_path, encoding="utf-8")

    raise ValueError("Unsupported document type. Please upload PDF, DOCX, or TXT.")


def ingest_document(file_path: str) -> str:
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

    db_path = os.path.join(BASE_DB_PATH, str(uuid.uuid4()))

    Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory=db_path
    )

    print("\nVector Database Created.")
    print(f"DB Path: {db_path}\n")

    return db_path