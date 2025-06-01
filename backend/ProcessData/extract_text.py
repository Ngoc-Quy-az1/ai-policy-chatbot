import pdfplumber
import docx
import pandas as pd
import tabula
import cv2
import numpy as np
from PIL import Image
import pytesseract
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import os

@dataclass
class DocumentElement:
    type: str  # 'text', 'table', 'chart'
    content: Any
    page_number: int
    metadata: Optional[Dict] = None

def extract_tables_from_pdf(pdf_path: str) -> List[DocumentElement]:
    """Extract tables from PDF using tabula-py"""
    tables = []
    try:
        # Read all tables from the PDF
        dfs = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)
        for page_num, df in enumerate(dfs, 1):
            if not df.empty:
                # Convert DataFrame to dictionary for better serialization
                table_dict = {
                    'data': df.to_dict(orient='records'),
                    'columns': df.columns.tolist(),
                    'shape': df.shape
                }
                tables.append(DocumentElement(
                    type='table',
                    content=table_dict,
                    page_number=page_num,
                    metadata={'table_index': len(tables)}
                ))
    except Exception as e:
        print(f"Error extracting tables: {str(e)}")
    return tables

def ensure_charts_dir():
    """Tạo thư mục lưu trữ biểu đồ nếu chưa tồn tại"""
    charts_dir = "./extracted_charts"
    if not os.path.exists(charts_dir):
        os.makedirs(charts_dir)
        print(f"Đã tạo thư mục {charts_dir}")
    return charts_dir

def extract_charts_from_pdf(pdf_path: str) -> List[DocumentElement]:
    """Extract charts from PDF using OpenCV and Tesseract"""
    charts = []
    try:
        # Tạo thư mục lưu trữ biểu đồ
        charts_dir = ensure_charts_dir()
        
        with pdfplumber.open(pdf_path) as pdf:
            # Lấy tên file PDF không có phần mở rộng
            pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
            
            for page_num, page in enumerate(pdf.pages, 1):
                # Convert page to image
                img = page.to_image()
                img_array = np.array(img.original)
                
                # Convert to grayscale
                gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
                
                # Apply threshold to get binary image
                _, binary = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
                
                # Find contours
                contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                # Get page dimensions
                height, width = img_array.shape[:2]
                page_area = height * width
                
                for idx, contour in enumerate(contours):
                    # Calculate contour properties
                    area = cv2.contourArea(contour)
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = float(w)/h if h > 0 else 0
                    
                    # Filter contours based on multiple criteria
                    if (area > 10000 and  # Minimum area
                        area < page_area * 0.8 and  # Maximum area (80% of page)
                        0.2 < aspect_ratio < 5 and  # Reasonable aspect ratio
                        w > 100 and h > 100):  # Minimum dimensions
                        
                        # Extract the region
                        chart_img = img_array[y:y+h, x:x+w]
                        
                        # Check if the region contains enough non-white pixels
                        non_white_pixels = np.sum(chart_img < 240)
                        if non_white_pixels > (w * h * 0.1):  # At least 10% non-white pixels
                            
                            # Tạo tên file ảnh với định dạng: pdf_name_page_chart.png
                            chart_filename = f"{pdf_name}_page{page_num}_chart{idx}.png"
                            chart_path = os.path.join(charts_dir, chart_filename)
                            
                            # Save chart image
                            cv2.imwrite(chart_path, chart_img)
                            
                            # Extract text from chart using OCR
                            try:
                                chart_text = pytesseract.image_to_string(chart_img, lang='eng+vie')
                            except:
                                chart_text = "Không thể trích xuất text từ biểu đồ"
                            
                            # Add to charts list
                            charts.append(DocumentElement(
                                type='chart',
                                content={
                                    'image_path': chart_path,
                                    'text': chart_text,
                                    'position': {'x': x, 'y': y, 'width': w, 'height': h},
                                    'properties': {
                                        'area': area,
                                        'aspect_ratio': aspect_ratio,
                                        'non_white_ratio': non_white_pixels / (w * h)
                                    }
                                },
                                page_number=page_num,
                                metadata={'chart_index': idx}
                            ))
    except Exception as e:
        print(f"Error extracting charts: {str(e)}")
    return charts

def extract_from_pdf(pdf_path: str) -> List[DocumentElement]:
    """Extract all elements (text, tables, charts) from PDF"""
    elements = []
    
    # Extract text
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            text = page.extract_text()
            if text:
                elements.append(DocumentElement(
                    type='text',
                    content=text,
                    page_number=page_num
                ))
    
    # Extract tables
    tables = extract_tables_from_pdf(pdf_path)
    elements.extend(tables)
    
    # Extract charts
    charts = extract_charts_from_pdf(pdf_path)
    elements.extend(charts)
    
    # Sort elements by page number
    elements.sort(key=lambda x: x.page_number)
    return elements

def extract_from_docx(path: str) -> List[DocumentElement]:
    """Extract elements from DOCX file"""
    elements = []
    doc = docx.Document(path)
    
    for page_num, paragraph in enumerate(doc.paragraphs, 1):
        if paragraph.text.strip():
            elements.append(DocumentElement(
                type='text',
                content=paragraph.text,
                page_number=page_num
            ))
    
    # Extract tables from DOCX
    for table_num, table in enumerate(doc.tables, 1):
        table_data = []
        for row in table.rows:
            table_data.append([cell.text for cell in row.cells])
        
        if table_data:
            elements.append(DocumentElement(
                type='table',
                content={
                    'data': table_data,
                    'shape': (len(table_data), len(table_data[0]) if table_data else 0)
                },
                page_number=table_num,
                metadata={'table_index': table_num}
            ))
    
    return elements
