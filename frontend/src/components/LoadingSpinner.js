import React from 'react';
import './LoadingSpinner.css';

const LoadingSpinner = () => {
  return (
    <div className="loading-spinner">
      <div className="spinner"></div>
      <div className="loading-text">Đang xử lý...</div>
    </div>
  );
};

export default LoadingSpinner; 