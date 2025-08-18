import fitz  
import io
from PIL import Image
import numpy as np
import easyocr

# PDF file path
pdf_path = "test.pdf"

# Open PDF
doc = fitz.open(pdf_path)

# Initialize EasyOCR Reader
reader = easyocr.Reader(['en'])

# Loop through each page
for page_num in range(len(doc)):
    page = doc[page_num]
    pix = page.get_pixmap()

    # Export to PNG bytes
    img_bytes = pix.tobytes("png")
    img = Image.open(io.BytesIO(img_bytes))

    # Convert PIL Image to NumPy array
    img_np = np.array(img)

    # Run OCR
    results = reader.readtext(img_np)

    # Extract text
    extracted_text = "\n".join([res[1] for res in results])

    print(f"\n--- Page {page_num+1} ---\n")
    print(extracted_text)
    print("\n" + "-"*40)
