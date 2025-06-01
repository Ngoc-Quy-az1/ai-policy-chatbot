import React from 'react';
import './ChatHistory.css';

const ChatHistory = ({ conversations, onSelectConversation, activeConversationId }) => {
  // Nhóm các cuộc hội thoại theo ngày
  const groupedConversations = conversations.reduce((groups, conv) => {
    const date = new Date(conv.date).toLocaleDateString('vi-VN');
    if (!groups[date]) {
      groups[date] = [];
    }
    groups[date].push(conv);
    return groups;
  }, {});

  return (
    <div className="chat-history">
      <div className="chat-history-header">
        <h3>Lịch sử hội thoại</h3>
      </div>
      <div className="chat-history-list">
        {Object.entries(groupedConversations).map(([date, convs]) => (
          <div key={date} className="chat-history-group">
            <div className="chat-history-date">{date}</div>
            {convs.map((conv) => (
              <div
                key={conv.id}
                className={`chat-history-item ${conv.id === activeConversationId ? 'active' : ''}`}
                onClick={() => onSelectConversation(conv.id)}
              >
                <div className="chat-history-preview">
                  <div className="chat-history-question">
                    {conv.first_message || 'Cuộc hội thoại mới'}
                  </div>
                  <div className="chat-history-time">
                    {new Date(conv.date).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
};

export default ChatHistory; 