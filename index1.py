import re
import os
import io
from flask import Flask, request, send_file
from PyPDF2 import PdfReader, PdfWriter
from pdfminer.high_level import extract_text
from PIL import Image
import pytesseract
import cv2

app = Flask(_name_)

# Function to extract text from a PDF
def extract_text_from_pdf(pdf_path):
    text = extract_text(pdf_path)
    return text

# Function to mask sensitive information in text
def mask_sensitive_info(text):
    patterns = {
        "phone": r'\b\d{10}\b',
        "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "name": r'\b[A-Z][a-z]* [A-Z][a-z]*\b',  # Example simple name pattern
        "clinic": r'\b[A-Z][a-z]* Clinic\b'      # Example simple clinic name pattern
    }
    
    for key, pattern in patterns.items():
        text = re.sub(pattern, "[MASKED]", text)
    return text

# Function to extract text from an image using OCR
def extract_text_from_image(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text

# Function to mask text in an image
def mask_text_in_image(image_path, text_positions):
    image = cv2.imread(image_path)
    for (x, y, w, h) in text_positions:
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 0), -1)
    masked_image_path = "masked_" + os.path.basename(image_path)
    cv2.imwrite(masked_image_path, image)
    return masked_image_path

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    pdf_path = os.path.join("uploads", file.filename)
    file.save(pdf_path)
    
    # Extract text from the PDF
    text = extract_text_from_pdf(pdf_path)
    masked_text = mask_sensitive_info(text)
    
    # Process each page for images and mask text in images
    masked_images = []
    reader = PdfReader(pdf_path)
    writer = PdfWriter()
    
    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        x_objects = page.get("/Resources").get("/XObject")
        if x_objects:
            for obj in x_objects:
                x_object = x_objects[obj]
                if x_object.get("/Subtype") == "/Image":
                    image_data = x_object.getData()
                    image_path = os.path.join("images", f"page_{page_num}image{obj}.png")
                    with open(image_path, "wb") as img_file:
                        img_file.write(image_data)
                    image_text = extract_text_from_image(image_path)
                    masked_image_text = mask_sensitive_info(image_text)
                    # Example positions, you'd need a function to find actual text positions
                    text_positions = [(50, 50, 100, 20)]  
                    masked_image_path = mask_text_in_image(image_path, text_positions)
                    masked_images.append(masked_image_path)
        
        writer.add_page(page)
    
    masked_pdf_path = os.path.join("masked_pdfs", "masked_" + file.filename)
    with open(masked_pdf_path, "wb") as masked_pdf:
        writer.write(masked_pdf)
    
    return send_file(masked_pdf_path, as_attachment=True)

if _name_ == "_main_":
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
    if not os.path.exists("images"):
        os.makedirs("images")
    if not os.path.exists("masked_pdfs"):
        os.makedirs("masked_pdfs")
    app.run()