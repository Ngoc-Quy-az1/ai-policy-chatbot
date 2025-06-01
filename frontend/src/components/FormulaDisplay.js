import React from 'react';
import 'katex/dist/katex.min.css';
import katex from 'katex';
import './FormulaDisplay.css';

const FormulaDisplay = ({ formula }) => {
  const renderFormula = () => {
    try {
      // Nếu công thức đã được wrap trong $ hoặc $$, giữ nguyên
      if (formula.startsWith('$') && formula.endsWith('$')) {
        return katex.renderToString(formula.slice(1, -1), {
          displayMode: false,
          throwOnError: false
        });
      }
      // Nếu công thức đã được wrap trong $$, render ở chế độ display
      if (formula.startsWith('$$') && formula.endsWith('$$')) {
        return katex.renderToString(formula.slice(2, -2), {
          displayMode: true,
          throwOnError: false
        });
      }
      // Mặc định wrap công thức trong $ và render inline
      return katex.renderToString(formula, {
        displayMode: false,
        throwOnError: false
      });
    } catch (error) {
      console.error('Error rendering formula:', error);
      return <div className="formula-error">Không thể hiển thị công thức</div>;
    }
  };

  return (
    <div className="formula-container">
      <div 
        className="formula-content"
        dangerouslySetInnerHTML={{ __html: renderFormula() }}
      />
    </div>
  );
};

export default FormulaDisplay; 