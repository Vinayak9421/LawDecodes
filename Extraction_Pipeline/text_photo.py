import warnings
import os
import fitz
import io
from PIL import Image
import numpy as np
import easyocr
from tqdm import tqdm
import argparse
from pathlib import Path

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")
os.environ['PYTHONWARNINGS'] = 'ignore'

class PDFTextExtractor:
    def __init__(self, languages=['en'], gpu=False, verbose=False):
        """
        Initialize PDF Text Extractor
        
        Args:
            languages (list): List of languages for OCR
            gpu (bool): Use GPU acceleration if available
            verbose (bool): Show detailed processing info
        """
        self.reader = easyocr.Reader(languages, gpu=gpu, verbose=verbose)
        self.verbose = verbose
    
    def extract_text_from_pdf(self, pdf_path, output_path=None, high_dpi=True, text_first=True):
        """
        Extract text from PDF using OCR with fallback options
        
        Args:
            pdf_path (str): Path to PDF file
            output_path (str): Optional path to save extracted text
            high_dpi (bool): Use higher resolution for better OCR
            text_first (bool): Try direct text extraction before OCR
            
        Returns:
            str: Extracted text from all pages
        """
        # Check if file exists
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        print(f"Processing PDF: {pdf_path}")
        
        try:
            doc = fitz.open(pdf_path)
            all_text = []
            total_pages = len(doc)
            
            print(f"Total pages: {total_pages}")
            
            # Process each page with progress bar
            for page_num in tqdm(range(total_pages), desc="Processing pages"):
                try:
                    page = doc[page_num]
                    extracted_text = ""
                    
                    # Try direct text extraction first
                    if text_first:
                        direct_text = page.get_text().strip()
                        if direct_text:
                            extracted_text = direct_text
                            if self.verbose:
                                print(f"Page {page_num + 1}: Used direct text extraction")
                        else:
                            # Fall back to OCR
                            extracted_text = self._ocr_page(page, high_dpi)
                            if self.verbose:
                                print(f"Page {page_num + 1}: Used OCR (no direct text found)")
                    else:
                        # Use OCR directly
                        extracted_text = self._ocr_page(page, high_dpi)
                        if self.verbose:
                            print(f"Page {page_num + 1}: Used OCR")
                    
                    # Add page separator and text
                    page_text = f"--- Page {page_num + 1} ---\n{extracted_text}"
                    all_text.append(page_text)
                    
                except Exception as e:
                    error_msg = f"Error processing page {page_num + 1}: {str(e)}"
                    print(error_msg)
                    all_text.append(f"--- Page {page_num + 1} ---\n[ERROR: {str(e)}]")
                    continue
            
            doc.close()
            
            # Combine all text
            final_text = "\n\n".join(all_text)
            
            # Save to file if requested
            if output_path:
                self.save_text(final_text, output_path)
                print(f"Text saved to: {output_path}")
            
            return final_text
            
        except Exception as e:
            print(f"Error opening PDF: {str(e)}")
            return None
    
    def _ocr_page(self, page, high_dpi=True):
        """
        Perform OCR on a single PDF page
        
        Args:
            page: PyMuPDF page object
            high_dpi (bool): Use higher resolution for better accuracy
            
        Returns:
            str: Extracted text from the page
        """
        # Set DPI scaling for better OCR accuracy
        if high_dpi:
            matrix = fitz.Matrix(2, 2)  # 2x scaling for better quality
            pix = page.get_pixmap(matrix=matrix)
        else:
            pix = page.get_pixmap()
        
        # Convert to PIL Image
        img_bytes = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_bytes))
        
        # Optional: Apply image preprocessing for better OCR
        img = self._preprocess_image(img)
        
        # Convert to NumPy array for EasyOCR
        img_np = np.array(img)
        
        # Run OCR
        try:
            results = self.reader.readtext(img_np)
            extracted_text = "\n".join([res[1] for res in results])
            return extracted_text
        except Exception as e:
            return f"[OCR Error: {str(e)}]"
    
    def _preprocess_image(self, img):
        """
        Apply basic image preprocessing to improve OCR accuracy
        
        Args:
            img: PIL Image object
            
        Returns:
            PIL Image: Preprocessed image
        """
        # Convert to RGB if not already
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Optional: Apply additional preprocessing here
        # - Contrast enhancement
        # - Noise reduction
        # - Deskewing
        
        return img
    
    def save_text(self, text, output_path):
        """
        Save extracted text to file
        
        Args:
            text (str): Text to save
            output_path (str): Output file path
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
        except Exception as e:
            print(f"Error saving file: {str(e)}")
    
    def batch_process(self, pdf_directory, output_directory=None):
        """
        Process multiple PDF files in a directory
        
        Args:
            pdf_directory (str): Directory containing PDF files
            output_directory (str): Directory to save text files
        """
        pdf_dir = Path(pdf_directory)
        pdf_files = list(pdf_dir.glob("*.pdf"))
        
        if not pdf_files:
            print(f"No PDF files found in {pdf_directory}")
            return
        
        print(f"Found {len(pdf_files)} PDF files")
        
        for pdf_file in pdf_files:
            print(f"\nProcessing: {pdf_file.name}")
            
            # Set output path
            if output_directory:
                output_dir = Path(output_directory)
                output_dir.mkdir(exist_ok=True)
                output_path = output_dir / f"{pdf_file.stem}_extracted.txt"
            else:
                output_path = pdf_file.parent / f"{pdf_file.stem}_extracted.txt"
            
            # Extract text
            try:
                text = self.extract_text_from_pdf(str(pdf_file), str(output_path))
                if text:
                    print(f"✅ Successfully processed: {pdf_file.name}")
                else:
                    print(f"❌ Failed to process: {pdf_file.name}")
            except Exception as e:
                print(f"❌ Error processing {pdf_file.name}: {str(e)}")

def main():
    """
    Main function with command-line interface
    """
    parser = argparse.ArgumentParser(description="Extract text from PDF files using OCR")
    parser.add_argument("pdf_path", help="Path to PDF file or directory")
    parser.add_argument("-o", "--output", help="Output file/directory path")
    parser.add_argument("-l", "--languages", nargs="+", default=["en"], 
                       help="Languages for OCR (default: en)")
    parser.add_argument("--gpu", action="store_true", help="Use GPU acceleration")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--no-text-first", action="store_true", 
                       help="Skip direct text extraction, use OCR only")
    parser.add_argument("--low-dpi", action="store_true", 
                       help="Use lower DPI for faster processing")
    parser.add_argument("--batch", action="store_true", 
                       help="Process all PDFs in directory")
    
    args = parser.parse_args()
    
    # Initialize extractor
    extractor = PDFTextExtractor(
        languages=args.languages,
        gpu=args.gpu,
        verbose=args.verbose
    )
    
    try:
        if args.batch:
            # Batch processing
            extractor.batch_process(args.pdf_path, args.output)
        else:
            # Single file processing
            text = extractor.extract_text_from_pdf(
                pdf_path=args.pdf_path,
                output_path=args.output,
                high_dpi=not args.low_dpi,
                text_first=not args.no_text_first
            )
            
            if text and not args.output:
                print("\n" + "="*50)
                print("EXTRACTED TEXT")
                print("="*50)
                print(text)
                
    except Exception as e:
        print(f"Error: {str(e)}")

# Simple usage example
def simple_usage():
    """
    Simple usage example for direct script execution
    """
    # PDF file path
    pdf_path = "test.pdf"
    
    # Initialize extractor
    extractor = PDFTextExtractor(languages=['en'], gpu=False, verbose=False)
    
    # Extract text
    try:
        text = extractor.extract_text_from_pdf(pdf_path, output_path="extracted_text.txt")
        
        if text:
            print("Text extraction completed successfully!")
            print(f"Extracted text preview:\n{text[:500]}...")
        else:
            print("Failed to extract text.")
            
    except FileNotFoundError:
        print(f"Error: PDF file '{pdf_path}' not found.")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    # Check if running with command line arguments
    import sys
    
    if len(sys.argv) > 1:
        main()  # Use command-line interface
    else:
        simple_usage()  # Use simple example
