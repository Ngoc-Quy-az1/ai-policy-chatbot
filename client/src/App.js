import React, { useState } from 'react';
import { 
  Container, 
  Box, 
  TextField, 
  Button, 
  Paper, 
  Typography,
  CircularProgress,
  Alert,
  Grid
} from '@mui/material';
import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

function App() {
  const [message, setMessage] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const result = await axios.post(`${API_URL}/chat`, { message });
      setResponse(result.data.response);
    } catch (error) {
      console.error('Error:', error);
      setError('Sorry, there was an error processing your request.');
    }
    setLoading(false);
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setLoading(true);
    setError('');
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const result = await axios.post(`${API_URL}/upload-pdf`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      setResponse('PDF processed successfully! You can now ask questions about the document.');
    } catch (error) {
      console.error('Error:', error);
      setError('Error uploading PDF file.');
    }
    setLoading(false);
  };

  const handleProcessDefault = async () => {
    setLoading(true);
    setError('');
    try {
      const result = await axios.post(`${API_URL}/process-default`);
      setResponse('Tài liệu ICT205_ASS.pdf đã được xử lý thành công! Bạn có thể đặt câu hỏi về tài liệu này.');
    } catch (error) {
      console.error('Error:', error);
      setError('Lỗi khi xử lý tài liệu mặc định.');
    }
    setLoading(false);
  };

  return (
    <Container maxWidth="md">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          AI Policy Chatbot
        </Typography>
        
        <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
          <Grid container spacing={2} sx={{ mb: 2 }}>
            <Grid item xs={6}>
              <Button
                variant="contained"
                component="label"
                fullWidth
              >
                Upload PDF
                <input
                  type="file"
                  hidden
                  accept=".pdf"
                  onChange={handleFileUpload}
                />
              </Button>
            </Grid>
            <Grid item xs={6}>
              <Button
                variant="contained"
                color="secondary"
                fullWidth
                onClick={handleProcessDefault}
                disabled={loading}
              >
                Xử lý tài liệu mặc định
              </Button>
            </Grid>
          </Grid>

          <form onSubmit={handleSubmit}>
            <TextField
              fullWidth
              multiline
              rows={4}
              variant="outlined"
              label="Ask your question"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              sx={{ mb: 2 }}
            />
            <Button 
              variant="contained" 
              color="primary" 
              type="submit"
              disabled={loading || !message.trim()}
              fullWidth
            >
              {loading ? <CircularProgress size={24} /> : 'Send'}
            </Button>
          </form>
        </Paper>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {response && (
          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Response:
            </Typography>
            <Typography>
              {response}
            </Typography>
          </Paper>
        )}
      </Box>
    </Container>
  );
}

export default App;
