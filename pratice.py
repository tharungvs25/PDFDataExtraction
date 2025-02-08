from flask import Flask, request, send_file
import fitz  # PyMuPDF
import pytesseract
import re
import io
from PIL import Image
import numpy as np
import cv2

app = Flask(_name_)

# Set the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\KRISHNA KALYAN\Downloads\Tesseract OCR'  # Update this path as per your installation

# HTML Template
HTML_TEMPLATE = '''
<!doctype html>
<html lang="en">
  <head>
    <title>PDF and Image Masking</title>
  </head>
  <body>
    <h1>Upload PDF or Image for Masking Sensitive Information</h1>
    <form action="/upload" method="post" enctype="multipart/form-data">
      <input type="file" name="file">
      <input type="submit" value="Upload">
    </form>
  </body>
</html>
'''

@app.route('/')
def index():
    return HTML_TEMPLATE

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    filename = file.filename

    if filename.endswith('.pdf'):
        return process_pdf(file)
    else:
        return process_image(file)

def process_pdf(file):
    file_stream = io.BytesIO(file.read())
    
    doc = fitz.open(stream=file_stream, filetype="pdf")
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text_blocks = page.get_text("dict")["blocks"]
        
        # Cover sensitive information
        cover_sensitive_info(page, text_blocks)
    
    output_stream = io.BytesIO()
    doc.save(output_stream)
    output_stream.seek(0)

    return send_file(output_stream, as_attachment=True, download_name='masked.pdf', mimetype='application/pdf')

def process_image(file):
    image = Image.open(file)
    text = pytesseract.image_to_string(image)
    
    # Mask sensitive information in the image using OpenCV
    image_np = np.array(image)
    for (x, y, w, h) in detect_sensitive_info(text, image_np):
        cv2.rectangle(image_np, (x, y), (x + w, y + h), (0, 0, 0), -1)
    
    # Convert back to PIL image and save to BytesIO
    image_pil = Image.fromarray(image_np)
    output_stream = io.BytesIO()
    image_pil.save(output_stream, format='PNG')
    output_stream.seek(0)

    return send_file(output_stream, as_attachment=True, download_name='masked_image.png', mimetype='image/png')

def cover_sensitive_info(page, text_blocks):
    for block in text_blocks:
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                text = span.get("text", "")
                bbox = span.get("bbox", [])
                if contains_sensitive_info(text):
                    # Draw a black rectangle over sensitive text
                    page.draw_rect(fitz.Rect(bbox[0], bbox[1], bbox[2], bbox[3]), color=(0, 0, 0), fill=True)

def contains_sensitive_info(text):
    patterns = [
        r'\b(Mr|Mrs|Ms)\.?\s[A-Z][a-z]+\s[A-Z][a-z]+\b',  # Names
        r'\b\d{3}[-.\s]??\d{3}[-.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-.\s]??\d{4}|\d{3}[-.\s]??\d{4}\b',  # Phone numbers
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email addresses
        r'\b\d{1,3}\s[A-Za-z0-9\s]+(?:Avenue|Ave|Street|St|Road|Rd|Boulevard|Blvd)\b'  # Addresses
    ]
    for pattern in patterns:
        if re.search(pattern, text):
            return True
    return False

def detect_sensitive_info(text, image_np):
    # Dummy function, as actual implementation depends on OCR results
    # Return list of rectangles where sensitive info is detected
    return []

if _name_ == "_main_":
    app.run(debug=True)