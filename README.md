# AI Policy Chatbot

A chatbot application that helps users understand policy documents using AI. Built with Python (Flask) backend and React frontend.

## Features

- Modern UI with Material-UI
- Real-time chat interface
- PDF document processing
- AI-powered responses using OpenAI and LangChain
- Vector database for efficient document retrieval
- Default policy document (ICT205_ASS.pdf) support

## Prerequisites

- Python (v3.8 or higher)
- Node.js (v14 or higher)
- npm (v6 or higher)
- OpenAI API key

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ai-policy-chatbot
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Install React frontend dependencies:
```bash
cd client
npm install
```

4. Create a .env file in the root directory with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

## Project Structure

```
ai-policy-chatbot/
├── client/                 # React frontend
│   ├── src/
│   │   ├── App.js         # Main React component
│   │   └── ...
│   └── package.json
├── app.py                 # Flask backend
├── chatbot.py            # Chatbot logic
├── load_documents.py     # PDF processing
├── extract_text.py       # Text extraction utilities
├── ICT205_ASS.pdf       # Default policy document
├── requirements.txt      # Python dependencies
└── .env                  # Environment variables
```

## Running the Application

1. Start the Python backend server:
```bash
python app.py
```

2. In a new terminal, start the React frontend:
```bash
cd client
npm start
```

3. Open your browser and navigate to `http://localhost:3000`

## How It Works

1. **Document Processing**:
   - Upload PDF through the web interface or use the default policy document
   - Backend processes and splits the document
   - Text chunks are converted to embeddings
   - Embeddings are stored in ChromaDB

2. **Chat Interface**:
   - User sends a question through React frontend
   - Flask backend processes the request
   - Python retrieves relevant document chunks
   - OpenAI generates a response
   - Response is displayed in the chat interface

## Using the Default Policy Document

The application includes a default policy document (ICT205_ASS.pdf) that can be processed with a single click:

1. Click the "Xử lý tài liệu mặc định" button in the interface
2. Wait for the processing to complete
3. Start asking questions about the policy document

## Technologies Used

- Backend:
  - Python & Flask
  - LangChain
  - OpenAI API
  - ChromaDB

- Frontend:
  - React
  - Material-UI
  - Axios

## Troubleshooting

1. **ChromaDB Issues**:
   - Make sure the `chroma_db` directory exists
   - Check if documents are properly processed

2. **OpenAI API Issues**:
   - Verify your API key in .env file
   - Check API rate limits

3. **PDF Processing Issues**:
   - Ensure PDF is readable and not corrupted
   - Check if pdfplumber is properly installed

4. **CORS Issues**:
   - Verify Flask-CORS is properly installed
   - Check if frontend is making requests to correct backend URL

## License

MIT 