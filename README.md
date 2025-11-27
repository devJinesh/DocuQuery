# DocuQuery - AI-Powered Document Q&A

An AI-powered PDF document analysis application with Retrieval-Augmented Generation (RAG). Chat with your PDFs using OpenAI-compatible APIs with multimodal content extraction and semantic search.

## Features

- PDF processing with text, table, and image extraction
- Semantic search using FAISS vector store with sentence transformers
- RAG-based question answering with citations
- Modern React frontend with dark mode
- Flexible API configuration (OpenAI, NVIDIA, or any compatible API)
- Runtime API settings through UI without restarting
- Conversation management with multi-turn support

## Tech Stack

**Backend:**
- FastAPI (Python web framework)
- SQLAlchemy (database ORM)
- FAISS (vector similarity search)
- Sentence Transformers (embeddings)
- PyMuPDF & pdfplumber (PDF processing)
- OpenAI client (compatible with any OpenAI-like API)

**Frontend:**
- React 18
- Tailwind CSS
- Lucide React (icons)
- Axios (HTTP client)

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 14+
- Git

### Installation

1. Clone the repository:
```bash
git clone https://github.com/devJinesh/DocuQuery.git
cd DocuQuery
```

2. Backend setup:
```bash
cd backend
python -m venv venv

# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt

# Create .env file
copy .env.example .env  # Windows
cp .env.example .env    # Mac/Linux
```

3. Configure your `.env` file:
```env
APP_NAME=DocuQuery
DATABASE_URL=sqlite+aiosqlite:///./data/docuquery.db

# LLM Configuration
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://integrate.api.nvidia.com/v1
MODEL_NAME=nvidia/llama-3.1-nemotron-70b-instruct

# Optional
ALLOWED_ORIGINS=http://localhost:3000
MAX_FILE_SIZE_MB=50
```

4. Start the backend:
```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

5. Frontend setup (new terminal):
```bash
cd frontend
npm install
npm start
```

The application will open at `http://localhost:3000`

### Using the Application

1. **Upload a PDF**: Click the "Upload" tab and select a PDF file
2. **Chat**: Select a document from "Documents" tab, switch to "Chat" tab, and ask questions
3. **Configure API** (optional): Click the settings icon to customize API endpoint, key, and model
4. **Dark Mode**: Toggle with the moon/sun icon in the header

## Development

Quick start scripts are available:

**Setup (first time only):**
```bash
setup.bat    # Windows
./setup.sh   # Mac/Linux
```

**Start application:**
```bash
start.bat    # Windows
./start.sh   # Mac/Linux
```

## License

MIT License - feel free to use for personal or commercial projects.
