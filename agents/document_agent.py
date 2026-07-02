"""
agents/document_agent.py

Document Agent

Handles:
- PDF
- DOCX
- TXT

Uses the vector database created by document_loader.py
"""

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


def document_agent(state):

    print("\n========== Document Agent ==========\n")

    query = state["query"]
    db_path = state.get("db_path")

    print("Document Query :", query)
    print("Using DB :", db_path)

    if not db_path:

        return {
            **state,
            "tool_output": "No document has been uploaded.",
            "success": False,
            "error": "Document database not found."
        }

    try:

        vector_db = Chroma(
            persist_directory=db_path,
            embedding_function=embedding_model
        )

        retriever = vector_db.as_retriever(
            search_kwargs={"k": 5}
        )

        docs = retriever.invoke(query)

        print(f"Retrieved {len(docs)} chunks from document.")

        if not docs:

            return {
                **state,
                "tool_output": "No relevant information found in the uploaded document.",
                "success": True,
                "error": None
            }

        context = "\n\n".join(
            doc.page_content
            for doc in docs
        )

        return {
            **state,
            "tool_output": context,
            "success": True,
            "error": None
        }

    except Exception as e:

        return {
            **state,
            "tool_output": "",
            "success": False,
            "error": str(e)
        }


# ------------------------------
# Test
# ------------------------------

if __name__ == "__main__":

    test_state = {
        "query": "Summarize this document",
        "db_path": "vectordb"
    }

    result = document_agent(test_state)

    print("\nRetrieved Content:\n")
    print(result["tool_output"])