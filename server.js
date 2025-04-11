const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

dotenv.config();

const app = express();
const port = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());

// Route để xử lý chat
app.post('/api/chat', async (req, res) => {
  try {
    const { message } = req.body;
    
    // Gọi Python script để xử lý câu hỏi
    const pythonProcess = spawn('python', ['chatbot.py', message]);
    
    let result = '';
    let error = '';

    pythonProcess.stdout.on('data', (data) => {
      result += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
      error += data.toString();
    });

    pythonProcess.on('close', (code) => {
      if (code !== 0) {
        console.error('Python Error:', error);
        return res.status(500).json({ error: 'Error processing request' });
      }
      res.json({ response: result.trim() });
    });
  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Route để xử lý upload và parse PDF
app.post('/api/upload-pdf', async (req, res) => {
  try {
    const { filePath } = req.body;
    
    // Gọi Python script để xử lý PDF
    const pythonProcess = spawn('python', ['load_documents.py', filePath]);
    
    let result = '';
    let error = '';

    pythonProcess.stdout.on('data', (data) => {
      result += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
      error += data.toString();
    });

    pythonProcess.on('close', (code) => {
      if (code !== 0) {
        console.error('Python Error:', error);
        return res.status(500).json({ error: 'Error processing PDF' });
      }
      res.json({ message: 'PDF processed successfully' });
    });
  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({ error: 'Error processing PDF' });
  }
});

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
}); 