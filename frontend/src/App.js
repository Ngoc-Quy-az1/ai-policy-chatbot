import React, { useState } from 'react';
import {
  Container,
  Box,
  TextField,
  Paper,
  Typography,
  CircularProgress,
  IconButton,
  Button,
  CssBaseline
} from '@mui/material';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import SendIcon from '@mui/icons-material/Send';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

function App() {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [darkMode, setDarkMode] = useState(false);

  const theme = createTheme({
    palette: {
      mode: darkMode ? 'dark' : 'light',
    },
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!message.trim()) return;

    setLoading(true);
    setMessages([...messages, { type: 'user', text: message }]);

    try {
      const result = await axios.post(`${API_URL}/chat`, { message });
      setMessages([...messages, { type: 'user', text: message }, { type: 'bot', text: result.data.response }]);
    } catch (error) {
      console.error('Error:', error);
    }
    setLoading(false);
    setMessage('');
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container maxWidth="lg" sx={{ minHeight: '100vh', py: 4, display: 'flex', flexDirection: 'row', gap: 2 }}>
        {/* Sidebar */}
        <Box
          sx={{
            width: '25%',
            backgroundColor: 'background.paper',
            boxShadow: 3,
            borderRadius: 2,
            overflowY: 'auto',
            p: 2,
          }}
        >
          <Typography variant="h6" gutterBottom align="center">
            Lịch sử Chat
          </Typography>
          {[...Array(5)].map((_, i) => (
            <Paper
              key={i}
              sx={{
                p: 1,
                mb: 1,
                cursor: 'pointer',
                '&:hover': {
                  backgroundColor: 'action.hover',
                  transform: 'scale(1.05)',
                  transition: 'all 0.2s ease',
                },
              }}
            >
              <Typography variant="body2">Cuộc trò chuyện {i + 1}</Typography>
            </Paper>
          ))}
        </Box>

        {/* Main Chat Area */}
        <Box
          sx={{
            flex: 1,
            backgroundColor: 'background.paper',
            boxShadow: 3,
            borderRadius: 2,
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
            p: 2,
          }}
        >
          {/* Nút chuyển đổi sáng/tối */}
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
            <Button
              variant="outlined"
              startIcon={darkMode ? <Brightness7Icon /> : <Brightness4Icon />}
              onClick={() => setDarkMode(!darkMode)}
              sx={{
                borderRadius: '20px',
                '&:hover': { backgroundColor: darkMode ? '#ffd54f' : '#1976d2', color: '#fff' },
                transition: 'all 0.3s ease',
              }}
            >
              {darkMode ? 'Light Mode' : 'Dark Mode'}
            </Button>
          </Box>

          <Box>
            <Typography
              variant="h4"
              component="h1"
              gutterBottom
              align="center"
              sx={{ fontWeight: 'bold' }}
            >
              AI Policy Chatbot
            </Typography>
            <Box
              sx={{
                p: 3,
                borderRadius: 2,
                minHeight: 400,
                display: 'flex',
                flexDirection: 'column',
                overflowY: 'auto',
              }}
            >
              {messages.map((msg, index) => (
                <Box
                  key={index}
                  sx={{
                    alignSelf: msg.type === 'user' ? 'flex-end' : 'flex-start',
                    mb: 2,
                  }}
                >
                  <Paper
                    sx={{
                      p: 2,
                      bgcolor: msg.type === 'user' ? 'primary.main' : 'grey.300',
                      color: msg.type === 'user' ? '#fff' : '#000',
                      borderRadius: 2,
                      boxShadow: 3,
                    }}
                  >
                    <Typography>{msg.text}</Typography>
                  </Paper>
                </Box>
              ))}
              {loading && (
                <Box sx={{ alignSelf: 'flex-start', mb: 2 }}>
                  <CircularProgress />
                </Box>
              )}
            </Box>
          </Box>

          <Box
            component="form"
            onSubmit={handleSubmit}
            sx={{ mt: 2, display: 'flex', alignItems: 'center' }}
          >
            <TextField
              fullWidth
              variant="outlined"
              label="Ask your question"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              sx={{
                borderRadius: 2,
                mr: 1,
                backgroundColor: 'background.default',
                boxShadow: 2,
              }}
            />
            <IconButton
              type="submit"
              color="primary"
              disabled={loading || !message.trim()}
              sx={{
                backgroundColor: 'primary.main',
                '&:hover': { backgroundColor: 'primary.dark' },
                transition: 'all 0.3s ease',
              }}
            >
              <SendIcon />
            </IconButton>
          </Box>
        </Box>
      </Container>
    </ThemeProvider>
  );
}

export default App;