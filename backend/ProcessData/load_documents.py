import os
import sys
import json
from typing import List, Dict, Any, Union
from datetime import datetime

from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from extract_text import extract_from_pdf, DocumentElement

# Load biến môi trường
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

def convert_metadata_value(value: Any) -> Union[str, int, float, bool]:
    """Convert complex metadata values to supported types"""
    if isinstance(value, (str, int, float, bool)):
        return value
    elif isinstance(value, (list, tuple, dict)):
        return json.dumps(value, ensure_ascii=False)
    else:
        return str(value)

def convert_metadata(metadata: Dict[str, Any]) -> Dict[str, Union[str, int, float, bool]]:
    """Convert all metadata values to supported types"""
    return {k: convert_metadata_value(v) for k, v in metadata.items()}

def ensure_chroma_dir():
    chroma_dir = "./chroma_db"
    if not os.path.exists(chroma_dir):
        os.makedirs(chroma_dir)
        print(f" Đã tạo thư mục {chroma_dir}")
    return chroma_dir

def process_text_elements(elements: List[DocumentElement], splitter: RecursiveCharacterTextSplitter) -> List[Document]:
    """Process text elements with appropriate chunking"""
    docs = []
    for element in elements:
        if element.type == 'text':
            texts = splitter.split_text(element.content)
            for text in texts:
                docs.append(Document(
                    page_content=text,
                    metadata={
                        'type': 'text',
                        'page_number': element.page_number,
                        'element_index': elements.index(element)
                    }
                ))
    return docs

def process_table_elements(elements: List[DocumentElement]) -> List[Document]:
    """Process table elements with enhanced structured format"""
    docs = []
    for element in elements:
        if element.type == 'table':
            table_content = element.content
            table_text = f"Table {element.metadata['table_index']}:\n"
            
            # Add table title if available
            if 'title' in element.metadata:
                table_text += f"Title: {element.metadata['title']}\n"
            
            # Add table description if available
            if 'description' in element.metadata:
                table_text += f"Description: {element.metadata['description']}\n"
            
            # Add column information with descriptions if available
            table_text += "Columns:\n"
            for col in table_content['columns']:
                col_desc = element.metadata.get('column_descriptions', {}).get(col, '')
                table_text += f"- {col}: {col_desc}\n"
            
            # Add data with row numbers and formatting
            table_text += "\nData:\n"
            for idx, row in enumerate(table_content['data'], 1):
                row_text = f"Row {idx}: "
                row_items = []
                for col, val in zip(table_content['columns'], row):
                    row_items.append(f"{col}={val}")
                row_text += " | ".join(row_items)
                table_text += row_text + "\n"
            
            # Add summary statistics if available
            if 'summary' in element.metadata:
                table_text += f"\nSummary Statistics:\n{element.metadata['summary']}\n"
            
            # Convert metadata to supported types
            metadata = {
                'type': 'table',
                'page_number': element.page_number,
                'table_index': element.metadata['table_index'],
                'shape': json.dumps(table_content['shape']),  # Convert tuple to string
                'title': element.metadata.get('title', ''),
                'description': element.metadata.get('description', ''),
                'column_descriptions': json.dumps(element.metadata.get('column_descriptions', {})),
                'summary': element.metadata.get('summary', '')
            }
            
            docs.append(Document(
                page_content=table_text,
                metadata=convert_metadata(metadata)
            ))
    return docs

def process_chart_elements(elements: List[DocumentElement]) -> List[Document]:
    """Process chart elements with enhanced analysis and description"""
    docs = []
    for element in elements:
        if element.type == 'chart':
            chart_content = element.content
            chart_text = f"Chart {element.metadata['chart_index']}:\n"
            
            # Add chart title and type
            if 'title' in element.metadata:
                chart_text += f"Title: {element.metadata['title']}\n"
            if 'chart_type' in element.metadata:
                chart_text += f"Type: {element.metadata['chart_type']}\n"
            
            # Add detailed description
            chart_text += f"Description: {chart_content['text']}\n"
            
            # Add axis information
            if 'axes' in element.metadata:
                axes = element.metadata['axes']
                chart_text += "Axes Information:\n"
                if 'x_axis' in axes:
                    chart_text += f"X-axis: {axes['x_axis']['label']} ({axes['x_axis']['type']})\n"
                if 'y_axis' in axes:
                    chart_text += f"Y-axis: {axes['y_axis']['label']} ({axes['y_axis']['type']})\n"
            
            # Add data points and trends
            if 'data_points' in element.metadata:
                chart_text += "\nKey Data Points:\n"
                for point in element.metadata['data_points']:
                    chart_text += f"- {point['label']}: {point['value']}\n"
            
            if 'trends' in element.metadata:
                chart_text += "\nTrends:\n"
                for trend in element.metadata['trends']:
                    chart_text += f"- {trend}\n"
            
            # Add interpretation
            if 'interpretation' in element.metadata:
                chart_text += f"\nInterpretation:\n{element.metadata['interpretation']}\n"
            
            # Add position and image path
            chart_text += f"\nPosition: {json.dumps(chart_content['position'])}\n"
            chart_text += f"Image saved at: {chart_content['image_path']}"
            
            # Convert metadata to supported types
            metadata = {
                'type': 'chart',
                'page_number': element.page_number,
                'chart_index': element.metadata['chart_index'],
                'image_path': chart_content['image_path'],
                'title': element.metadata.get('title', ''),
                'chart_type': element.metadata.get('chart_type', ''),
                'axes': json.dumps(element.metadata.get('axes', {})),
                'data_points': json.dumps(element.metadata.get('data_points', [])),
                'trends': json.dumps(element.metadata.get('trends', [])),
                'interpretation': element.metadata.get('interpretation', '')
            }
            
            docs.append(Document(
                page_content=chart_text,
                metadata=convert_metadata(metadata)
            ))
    return docs

def process_formula_elements(elements: List[DocumentElement]) -> List[Document]:
    """Process formula elements with enhanced mathematical representation"""
    docs = []
    for element in elements:
        if element.type == 'formula':
            formula_content = element.content
            formula_text = f"Formula {element.metadata['formula_index']}:\n"
            
            # Add formula type
            formula_text += f"Type: {element.metadata['formula_type']}\n"
            
            # Add the formula in different representations
            formula_text += f"\nOriginal Formula: {formula_content['formula']}\n"
            formula_text += f"LaTeX Representation: {formula_content['latex']}\n"
            
            # Add variables
            if formula_content['variables']:
                formula_text += f"\nVariables: {', '.join(formula_content['variables'])}\n"
            
            # Add context
            formula_text += f"\nContext:\n{formula_content['context']}\n"
            
            # Add formula properties
            formula_text += "\nFormula Properties:\n"
            if element.metadata['has_equals']:
                formula_text += "- Contains equation\n"
            if element.metadata['has_fraction']:
                formula_text += "- Contains fraction\n"
            if element.metadata['has_power']:
                formula_text += "- Contains power/exponent\n"
            if element.metadata['has_subscript']:
                formula_text += "- Contains subscript\n"
            if element.metadata['has_square_root']:
                formula_text += "- Contains square root\n"
            
            # Convert metadata to supported types
            metadata = {
                'type': 'formula',
                'page_number': element.page_number,
                'formula_index': element.metadata['formula_index'],
                'formula_type': element.metadata['formula_type'],
                'variables': json.dumps(element.metadata['variables']),
                'has_equals': element.metadata['has_equals'],
                'has_fraction': element.metadata['has_fraction'],
                'has_power': element.metadata['has_power'],
                'has_subscript': element.metadata['has_subscript'],
                'has_square_root': element.metadata['has_square_root']
            }
            
            docs.append(Document(
                page_content=formula_text,
                metadata=convert_metadata(metadata)
            ))
    return docs

def process_pdf(pdf_path: str) -> str:
    """Process PDF file and store different types of elements in ChromaDB"""
    ensure_chroma_dir()
    
    # Extract all elements from PDF
    elements = extract_from_pdf(pdf_path)
    
    # Initialize text splitter for text content
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
    )
    
    # Process different types of elements
    text_docs = process_text_elements(elements, text_splitter)
    table_docs = process_table_elements(elements)
    chart_docs = process_chart_elements(elements)
    formula_docs = process_formula_elements(elements)
    
    # Combine all documents
    all_docs = text_docs + table_docs + chart_docs + formula_docs
    
    # Create embeddings and store in ChromaDB
    embedding = OpenAIEmbeddings(api_key=api_key)
    vectorstore = Chroma.from_documents(
        documents=all_docs,
        embedding=embedding,
        persist_directory="./chroma_db"
    )
    vectorstore.persist()
    
    return f"Đã xử lý và lưu {len(text_docs)} đoạn văn bản, {len(table_docs)} bảng, {len(chart_docs)} biểu đồ, và {len(formula_docs)} công thức vào ChromaDB."

if __name__ == "__main__":
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        result = process_pdf(pdf_path)
        print(result)
    else:
        default_pdf = "ICT205_ASS.pdf"
        if os.path.exists(default_pdf):
            result = process_pdf(default_pdf)
            print(result)
        else:
            print(f"File {default_pdf} không tồn tại. Vui lòng cung cấp đường dẫn đến file PDF.")
