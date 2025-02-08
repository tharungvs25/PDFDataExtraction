
from pdf2image import convert_from_path

# Replace with your PDF file path
pdf_path = "exe1.pdf"  

# Convert PDF to images
images = convert_from_path(pdf_path)

# Save each image as a JPEG file
for i, image in enumerate(images):
    image.save(f"page_{i+1}.jpg", "JPEG")