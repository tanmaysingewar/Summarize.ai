import os
from PyPDF2 import PdfReader
from docx import Document
from PyPDF2 import PdfReader
from pathlib import Path

def pdf_reader(file_path):
    reader = PdfReader(file_path)
    number_of_pages = len(reader.pages)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    os.remove(file_path)
    return text

def docx_reader(file_path):
    doc = Document(file_path)
    para = doc.paragraphs
    text = ""
    for p in para:
        text += p.text
    os.remove(file_path)
    return text

def txt_reader(file_path):
    with open(file_path, "r") as f:
        text = f.read()
    os.remove(file_path)
    return text




__all__ = ["pdf_reader", "docx_reader", "txt_reader"]