import React from 'react';
import './TableDisplay.css';

const TableDisplay = ({ tableData }) => {
  try {
    // Parse table data từ string sang JSON nếu cần
    const data = typeof tableData === 'string' ? JSON.parse(tableData) : tableData;
    
    // Kiểm tra cấu trúc bảng
    if (!data.columns || !data.data) {
      return <div className="table-error">Dữ liệu bảng không hợp lệ</div>;
    }

    return (
      <div className="table-container">
        <table className="data-table">
          <thead>
            <tr>
              {data.columns.map((column, index) => (
                <th key={index}>{column}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.data.map((row, rowIndex) => (
              <tr key={rowIndex}>
                {data.columns.map((column, colIndex) => (
                  <td key={colIndex}>{row[column]}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  } catch (error) {
    console.error('Error rendering table:', error);
    return <div className="table-error">Không thể hiển thị bảng</div>;
  }
};

export default TableDisplay; 