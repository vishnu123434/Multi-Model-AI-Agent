"""
agents/pdf_agent.py

PDF Agent

Retrieves relevant chunks from the uploaded PDF vector database
and keeps the retrieved context small.
"""

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


DB_PATH = "vectordb"
MAX_CHUNK_CHARS = 900


embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


def trim_chunk(text: str) -> str:
    if len(text) <= MAX_CHUNK_CHARS:
        return text

    return text[:MAX_CHUNK_CHARS] + "\n[Chunk trimmed.]"


def pdf_agent(state):

    print("\n========== PDF Agent ==========\n")

    try:

        query = state["query"]

        print(f"PDF Query : {query}")

        vector_db = Chroma(
            persist_directory=DB_PATH,
            embedding_function=embedding_model
        )

        retriever = vector_db.as_retriever(
            search_kwargs={
                "k": 3
            }
        )

        docs = retriever.invoke(query)

        if not docs:

            return {
                **state,
                "tool_output": "No relevant information found in the uploaded PDF.",
                "response": None,
                "success": False,
                "error": "No relevant PDF content found."
            }

        context_parts = []

        for i, doc in enumerate(docs, start=1):
            page = doc.metadata.get("page", 0) + 1
            content = trim_chunk(doc.page_content)

            context_parts.append(
                f"PDF Chunk {i} | Page {page}\n{content}"
            )

        context = "\n\n".join(context_parts)

        print(f"Retrieved {len(docs)} chunks from PDF.")

        return {
            **state,
            "tool_output": context,
            "response": None,
            "success": True,
            "error": None
        }

    except Exception as e:

        return {
            **state,
            "tool_output": "",
            "response": None,
            "success": False,
            "error": str(e)
        }