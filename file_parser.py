import pytesseract
from PIL import Image
import pdfplumber
import docx

def extract_text_from_file(file_path):
    ext = file_path.split('.')[-1].lower()
    
    if ext in ['jpg', 'jpeg', 'png']:
        return pytesseract.image_to_string(Image.open(file_path))
    
    elif ext == 'pdf':
        with pdfplumber.open(file_path) as pdf:
            return '\n'.join([page.extract_text() or "" for page in pdf.pages])
    
    elif ext == 'docx':
        doc = docx.Document(file_path)
        return '\n'.join([p.text for p in doc.paragraphs])
    
    return "Unsupported file type."