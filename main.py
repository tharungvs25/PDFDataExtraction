import cv2
import pytesseract
import numpy as np
import re
import pandas as pd
import os
import sys
from pdf2image import convert_from_path

# Assuming Tesseract is installed and configured correctly
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Update this path if needed

def image_to_text(image_path):
    """
    Extracts text from an image using OpenCV and Tesseract OCR.

    Args:
        image_path (str): Path to the image file.

    Returns:
        str: Extracted text from the image.
    """
    try:
        image = cv2.imread(image_path)
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        thresh = cv2.adaptiveThreshold(image_gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
        text = pytesseract.image_to_string(thresh, config='--psm 6')
        return text
    except Exception as e:
        print(f"Error during image processing: {e}")
        return ""

def pdf_to_text(pdf_path):
    """
    Extracts text from a PDF file by converting each page to an image and then using Tesseract OCR.

    Args:
        pdf_path (str): Path to the PDF file.

    Returns:
        str: Extracted text from the PDF.
    """
    try:
        pages = convert_from_path(pdf_path)
        text = ""
        for page in pages:
            page_np = np.array(page)
            page_gray = cv2.cvtColor(page_np, cv2.COLOR_BGR2GRAY)
            thresh = cv2.adaptiveThreshold(page_gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
            text += pytesseract.image_to_string(thresh, config='--psm 6')
        return text
    except Exception as e:
        print(f"Error during PDF processing: {e}")
        return ""

def extract_data(extracted_text):
    """
    Extracts name, phone number, and address from the provided text using regular expressions.

    Args:
        extracted_text (str): Text extracted from the image.

    Returns:
        dict: Dictionary containing extracted data ('name', 'phone', 'address').
    """
    data = {}
    name_pattern = r"Name: (.*)"
    phone_pattern = r"Phone Number: (\d+)"
    address_pattern = r"Location: (.*)"

    name_match = re.search(name_pattern, extracted_text)
    if name_match:
        data['name'] = name_match.group(1).strip()
    else:
        print("Name not found in the text.")

    phone_match = re.search(phone_pattern, extracted_text)
    if phone_match:
        data['phone'] = phone_match.group(1)
    else:
        print("Phone number not found in the text.")

    address_match = re.search(address_pattern, extracted_text)
    if address_match:
        data['address'] = address_match.group(1).strip()
    else:
        print("Address not found in the text.")

    return data

def process_file(file_path):
    file_extension = os.path.splitext(file_path)[1].lower()
    
    if file_extension == '.jpg':
        extracted_text = image_to_text(file_path)
    elif file_extension == '.pdf':
        extracted_text = pdf_to_text(file_path)
    else:
        print("Unsupported file type. Please provide a JPG or PDF file.")
        return

    if extracted_text:
        data = extract_data(extracted_text)
        if data:
            df = pd.DataFrame([data])
            df.to_excel('extracted_data.xlsx', index=False)
            print("Extracted data saved to extracted_data.xlsx")
        else:
            print("No relevant data found in the extracted text.")
    else:
        print("No text extracted from the file.")

def main():
    file_path = input("Enter the file path: ")
    
    if not os.path.exists(file_path):
        print("File does not exist.")
        return
    
    process_file(file_path)

if __name__ == "__main__":
    main()
