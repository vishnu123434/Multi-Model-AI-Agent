# 🤖 Multi-Model AI Agent

A powerful Multi-Agent AI Assistant built using **LangGraph**, **Flask**, and **LLMs** that intelligently routes user queries to specialized AI agents.

## 🚀 Features

- 🌐 Live Web Search
- 💱 Universal Currency Conversion (150+ currencies)
- 📄 Document QA & Summarization (PDF, DOCX, TXT)
- 👁 OCR (Extract text from images)
- 🖼 Image Captioning
- 🧠 Multi-Agent Workflow using LangGraph
- 🔀 Intelligent Query Routing
- 💬 Interactive Chat Interface
- 📚 Vector Database (ChromaDB)
- 🤗 HuggingFace Embeddings
- ⚡ Groq LLM Integration

---

## 🏗 Project Architecture

```
User
   │
   ▼
Flask App
   │
   ▼
Planner Agent
   │
   ▼
Router Agent
   │
   ├──────────────► Web Search Agent
   │
   ├──────────────► Currency Agent
   │
   ├──────────────► Document QA Agent
   │
   ├──────────────► OCR Agent
   │
   └──────────────► Image Caption Agent
                     │
                     ▼
               Response Agent
                     │
                     ▼
                  Final Answer
```

---

## 📂 Project Structure

```
Multi-Model-AI-Agent/

├── agents/
├── models/
├── tools/
├── uploads/
├── vectordb/
├── templates/
├── static/
├── docs/
├── app.py
├── workflow.py
├── requirements.txt
└── README.md
```

---

## 🛠 Technologies Used

- Python
- Flask
- LangGraph
- LangChain
- ChromaDB
- HuggingFace Transformers
- Sentence Transformers
- EasyOCR
- Pillow
- Groq API
- DuckDuckGo Search
- HTML
- CSS
- JavaScript

---

## ⚙ Installation

Clone the repository

```bash
git clone https://github.com/vishnu123434/Multi-Model-AI-Agent.git
```

Go inside project

```bash
cd Multi-Model-AI-Agent
```

Create virtual environment

```bash
python -m venv venv
```

Activate

Windows

```bash
venv\Scripts\activate
```

Linux / Mac

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run

```bash
python app.py
```

---

## 📸 Features

### 🌐 Web Search

Search latest information from the web.

### 💱 Currency Converter

Supports 150+ international currencies.

Example:

```
Convert 200 USD to INR
```

```
500 Euros to Dollars
```

---

### 📄 Document QA

Supports

- PDF
- DOCX
- TXT

Ask questions directly from uploaded documents.

---

### 👁 OCR

Extract printed text from images.

---

### 🖼 Image Captioning

Generate AI captions for uploaded images.

---

## 🎯 Future Improvements

- Conversation Memory
- Maps & Places Agent
- Weather Agent
- Streaming Responses
- Docker Deployment
- Authentication
- Voice Support
- Image Question Answering

---

## 👨‍💻 Author

**K. Vishnu Vardhan Reddy**

GitHub

https://github.com/vishnu123434

LinkedIn

(Add your LinkedIn URL)

---

## ⭐ If you like this project, give it a Star.
