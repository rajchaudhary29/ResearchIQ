# ResearchIQ

App Link : https://researchiq-p5adittcqgn99zpoehuibi.streamlit.app/

An AI-powered app for reading research papers faster. Upload a PDF and get an automatic summary, a breakdown of the paper's key contributions, and a chat interface to ask questions directly about the content.

## Features

- **PDF upload** — drop in any research paper as a PDF.
- **Summary** — problem, main idea, method, results, and limitations, drawn from across the whole paper.
- **Contributions** — a focused breakdown of the paper's novel technical contributions.
- **Chat** — ask questions about the paper; answers are retrieved from the document with page references.

## Tech Stack

- [Streamlit](https://streamlit.io/) — UI
- [LangChain](https://www.langchain.com/) — orchestration
- [PyMuPDF](https://pymupdf.readthedocs.io/) — PDF text extraction
- [Sentence-Transformers](https://www.sbert.net/) — embeddings
- [FAISS](https://github.com/facebookresearch/faiss) — vector store
- [Mistral](https://mistral.ai/) — LLM

## Project Structure

```
ResearchIQ/
├── app.py              # Streamlit app
├── database.py         # Vector store creation
├── llm.py              # LLM client setup
├── prompts.py          # Prompt templates
├── requirements.txt    # Dependencies
├── vectorstore/        # Persisted vector store data
└── .env                # API keys (not committed)
```

## Setup

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file with:
```
MISTRAL_API_KEY=your_api_key_here
```

Run the app:
```
streamlit run app.py
```

## Usage

1. Upload a PDF.
2. Use the **Summary**, **Contributions**, and **Chat** tabs to explore it (Summary/Contributions generate on click).
3. Upload a new PDF anytime to reset and start fresh.
