import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import ChatHistory from './components/ChatHistory';
import ChatMessage from './components/ChatMessage';
import ChatInput from './components/ChatInput';
import LoadingSpinner from './components/LoadingSpinner';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [conversations, setConversations] = useState([]);
  const [activeConversationId, setActiveConversationId] = useState(null);
  const messagesEndRef = useRef(null);

  // Lấy danh sách cuộc hội thoại khi component mount
  useEffect(() => {
    fetchConversations();
  }, []);

  // Tự động cuộn xuống tin nhắn mới nhất
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchConversations = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/conversations');
      setConversations(response.data);
    } catch (error) {
      console.error('Error fetching conversations:', error);
    }
  };

  const handleSelectConversation = async (conversationId) => {
    try {
      const response = await axios.get(`http://localhost:5000/api/conversations/${conversationId}`);
      setMessages(response.data.messages);
      setActiveConversationId(conversationId);
    } catch (error) {
      console.error('Error fetching conversation:', error);
    }
  };

  const handleSendMessage = async (content) => {
    setIsLoading(true);
    const userMessage = {
      content,
      timestamp: new Date().toISOString(),
      isBot: false
    };

    setMessages(prev => [...prev, userMessage]);

    try {
      const response = await axios.post('http://localhost:5000/api/chat', {
        question: content,
        conversation_id: activeConversationId
      });

      // Truyền đầy đủ các trường từ response.data
      const botMessage = {
        content: response.data.answer,
        question: response.data.question,
        response_time: response.data.response_time,
        token_usage: response.data.token_usage,
        conversation_id: response.data.conversation_id,
        timestamp: response.data.timestamp,
        sources: response.data.sources,
        isBot: true
      };

      setMessages(prev => [...prev, botMessage]);

      // Cập nhật danh sách cuộc hội thoại
      if (!activeConversationId) {
        setActiveConversationId(response.data.conversation_id);
        await fetchConversations();
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        content: 'Xin lỗi, có lỗi xảy ra. Vui lòng thử lại sau.',
        timestamp: new Date().toISOString(),
        isBot: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const startNewConversation = () => {
    setMessages([]);
    setActiveConversationId(null);
  };

  return (
    <div className="app">
      <div className="chat-container">
        <ChatHistory
          conversations={conversations}
          onSelectConversation={handleSelectConversation}
          activeConversationId={activeConversationId}
        />
        <div className="chat-main">
          <div className="chat-header">
            <h2>Policy Chatbot</h2>
            <button onClick={startNewConversation} className="new-chat-button">
              Cuộc hội thoại mới
            </button>
          </div>
          <div className="chat-messages">
            {messages.map((message, index) => (
              <ChatMessage
                key={index}
                message={message}
                isBot={message.isBot}
              />
            ))}
            {isLoading && <LoadingSpinner />}
            <div ref={messagesEndRef} />
          </div>
          <ChatInput
            onSendMessage={handleSendMessage}
            isLoading={isLoading}
          />
        </div>
      </div>
    </div>
  );
}

export default App;