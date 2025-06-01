import React, { useEffect, useState } from 'react';
import TableDisplay from './TableDisplay';
import FormulaDisplay from './FormulaDisplay';
import LoadingSpinner from './LoadingSpinner';
import './ChatMessage.css';

const TYPING_SPEED = 18; // ms per character

const ChatMessage = ({ message, isBot, isLoading }) => {
  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('vi-VN', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const [displayedText, setDisplayedText] = useState(isBot && isLoading ? '' : message.content);

  useEffect(() => {
    if (isBot && isLoading) {
      setDisplayedText('');
      let i = 0;
      const interval = setInterval(() => {
        setDisplayedText((prev) => message.content.slice(0, i + 1));
        i++;
        if (i >= message.content.length) clearInterval(interval);
      }, TYPING_SPEED);
      return () => clearInterval(interval);
    } else {
      setDisplayedText(message.content);
    }
  }, [isBot, isLoading, message.content]);

  const formatContent = (content) => {
    // Chia nội dung thành các đoạn
    const paragraphs = content.split('\n').filter(p => p.trim());
    
    return paragraphs.map((paragraph, index) => {
      // Kiểm tra nếu đoạn văn quá dài, chia thành các câu
      if (paragraph.length > 100) {
        const sentences = paragraph.match(/[^.!?]+[.!?]+/g) || [paragraph];
        return (
          <div key={index} className="message-paragraph">
            {sentences.map((sentence, sIndex) => (
              <p key={sIndex} className="message-sentence">
                {sentence.trim()}
              </p>
            ))}
          </div>
        );
      }
      return <p key={index} className="message-paragraph">{paragraph}</p>;
    });
  };

  return (
    <div className={`chat-message ${isBot ? 'bot' : 'user'}`}>
      <div className="message-avatar">
        {isBot ? '🤖' : '👤'}
        {/* Spinner cạnh avatar khi bot đang loading */}
        {isBot && isLoading && <span style={{ marginLeft: 8 }}><LoadingSpinner size={22} /></span>}
      </div>
      <div className="message-content">
        <div className="message-text">
          {formatContent(displayedText)}
        </div>
        
        {/* Hiển thị bảng nếu có */}
        {isBot && message.table && (
          <TableDisplay tableData={message.table} />
        )}
        
        {/* Hiển thị công thức nếu có */}
        {isBot && message.formula && (
          <FormulaDisplay formula={message.formula} />
        )}
        
        {/* Hiển thị ảnh nếu có */}
        {isBot && message.image_path && (
          <div className="message-image">
            <img 
              src={message.image_path} 
              alt="Biểu đồ" 
              onError={(e) => {
                e.target.onerror = null;
                e.target.src = 'placeholder.png';
              }}
            />
          </div>
        )}
        
        {/* Hiển thị nguồn tham khảo nếu có */}
        {isBot && message.sources && (
          <div className="message-sources">
            <small>Nguồn tham khảo:</small>
            <ul>
              {message.sources.tables && (
                <li>Bảng: {message.sources.tables}</li>
              )}
              {message.sources.charts && (
                <li>Biểu đồ: {message.sources.charts}</li>
              )}
              {message.sources.formulas && (
                <li>Công thức: {message.sources.formulas}</li>
              )}
            </ul>
          </div>
        )}
        
        <div className="message-timestamp">
          {formatTimestamp(message.timestamp)}
        </div>
      </div>
    </div>
  );
};

export default ChatMessage; 