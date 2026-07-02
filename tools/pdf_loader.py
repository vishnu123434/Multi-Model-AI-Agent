"""
tools/pdf_loader.py

Loads uploaded PDF files,
splits them into chunks,
and stores them in ChromaDB.
"""

import os
import shutil

from langchain_community.document_loaders import PyPDFLoader

from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_chroma import Chroma

from langchain_huggingface import HuggingFaceEmbeddings


DB_PATH = "vectordb"


embedding_model = HuggingFaceEmbeddings(

    model_name="sentence-transformers/all-MiniLM-L6-v2"

)


def ingest_pdf(pdf_path):

    print("\nLoading PDF...\n")

    loader = PyPDFLoader(pdf_path)

    documents = loader.load()

    print(f"Loaded {len(documents)} pages.")

    splitter = RecursiveCharacterTextSplitter(

        chunk_size=1000,

        chunk_overlap=200

    )

    chunks = splitter.split_documents(documents)

    print(f"Created {len(chunks)} chunks.")

    # Remove previous DB

    if os.path.exists(DB_PATH):

        shutil.rmtree(DB_PATH)

    vector_db = Chroma.from_documents(

        documents=chunks,

        embedding=embedding_model,

        persist_directory=DB_PATH

    )

    print("\nVector Database Created.\n")

    return vector_db