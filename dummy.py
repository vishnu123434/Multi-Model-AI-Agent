from workflow import app

state = {
    "query": "Describe this image",
    "file_path": "uploads/images/sample1.jpg",
    "history": []
}

result = app.invoke(state)

print(result["response"])