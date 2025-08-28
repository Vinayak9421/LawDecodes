import easyocr
import cv2
import numpy as np

class OCRModel:
    """
    A reusable OCR model class that initializes the EasyOCR reader once for efficiency.
    """
    def __init__(self, languages=['mr', 'hi', 'en']):
        """
        Initializes the OCRModel. This is where the one-time, slow setup happens.
        
        Args:
            languages (list): A list of language codes to be loaded by EasyOCR.
        """
        print("Initializing OCR Model... (Loading language models into memory)")
        self.reader = easyocr.Reader(languages)
        print("OCR Model initialized and ready.")

    def extract_text(self, image_path: str, upscale_factor: int = 2, sharpen: bool = True, paragraph: bool = False, confidence_threshold: float = 0.4):
        """
        Performs OCR on an image using the pre-initialized model.

        Args:
            image_path (str): The path to the input image file.
            All other args are for tuning the extraction process.

        Returns:
            str: The concatenated, high-confidence text extracted from the image.
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                return f"ERROR: Could not load image at path: {image_path}"

            # --- Pre-processing Pipeline ---
            processed_image = image.copy()
            if upscale_factor > 1:
                processed_image = cv2.resize(processed_image, None, fx=upscale_factor, fy=upscale_factor, interpolation=cv2.INTER_CUBIC)

            if sharpen:
                sharpen_kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
                processed_image = cv2.filter2D(processed_image, -1, sharpen_kernel)

            # --- OCR Extraction using the pre-loaded reader ---
            results = self.reader.readtext(processed_image, detail=1, paragraph=paragraph)

            # --- Post-processing (Confidence Filtering) ---
            extracted_words = []
            for (bbox, text, confidence) in results:
                if confidence >= confidence_threshold:
                    extracted_words.append(text)

            return " ".join(extracted_words).strip()

        except Exception as e:
            return f"An unexpected error occurred in the OCR module: {e}"


if __name__ == '__main__':
    print("--- Testing the OCRModel class ---")
    
    # --- Step 1: Create an instance of the model. ---
    # This is the "slow" part that happens only ONCE.
    ocr_model = OCRModel(languages=['mr', 'hi', 'en'])

    # --- Step 2: Use the model as many times as you want. ---
    # This part is fast because the models are already in memory.
    
    print("\n--- Running on English Image ---")
    eng_image = 'test.png' 
    eng_text = ocr_model.extract_text(eng_image)
    print(eng_text)
    
    print("\n--- Running on Marathi Image with Custom Tuning ---")
    mar_image = 'testmar.png'
    mar_text = ocr_model.extract_text(
        mar_image, 
        upscale_factor=1, # This image is clean, no upscale needed
        sharpen=False,
        paragraph=False, 
        confidence_threshold=0.5
    )
    print(mar_text)
    
    print("\n--- Model test complete ---")