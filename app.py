import pytesseract
from pdf2image import convert_from_path
import fitz  # PyMuPDF
from PIL import Image
import os
import json
import datetime

pytesseract.pytesseract.tesseract_cmd = r'D:\\TesseractOCR\\tesseract.exe'
os.environ['TESSDATA_PREFIX'] = r'D:\\TesseractOCR\\tessdata'

class SimpleTextOCR:
    def __init__(self, tesseract_path=None, poppler_path=None):
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        self.poppler_path = poppler_path or r"D:\\poppler\\poppler-24.08.0\\Library\\bin"
    
    def perform_multiple_ocr(self, image, languages='eng'):
        """Perform OCR with different Tesseract configurations - no preprocessing"""
        results = {}
        
        # 1. Default OCR
        try:
            default_text = pytesseract.image_to_string(image, lang=languages)
            results['default'] = default_text.strip()
        except Exception as e:
            results['default'] = f"Error: {str(e)}"
        
        # 2. PSM 3 - Fully automatic page segmentation (default but explicit)
        try:
            psm3_text = pytesseract.image_to_string(image, lang=languages, config='--psm 3')
            results['auto_segmentation'] = psm3_text.strip()
        except Exception as e:
            results['auto_segmentation'] = f"Error: {str(e)}"
        
        # 3. PSM 11 - Sparse text
        try:
            psm11_text = pytesseract.image_to_string(image, lang=languages, config='--psm 11')
            results['sparse_text'] = psm11_text.strip()
        except Exception as e:
            results['sparse_text'] = f"Error: {str(e)}"
        
        # 4. OEM 1 - Neural nets LSTM engine only
        try:
            oem1_text = pytesseract.image_to_string(image, lang=languages, config='--oem 1 --psm 6')
            results['lstm_engine'] = oem1_text.strip()
        except Exception as e:
            results['lstm_engine'] = f"Error: {str(e)}"
        
        # 5. Character whitelist for numbers and dates
        try:
            numbers_config = '--psm 7 -c tessedit_char_whitelist=0123456789/.-: '
            numbers_text = pytesseract.image_to_string(image, lang=languages, config=numbers_config)
            results['numbers_only'] = numbers_text.strip()
        except Exception as e:
            results['numbers_only'] = f"Error: {str(e)}"
        
        # 5. Character whitelist for letters only
        try:
            letters_config = '--psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz '
            letters_text = pytesseract.image_to_string(image, lang=languages, config=letters_config)
            results['letters_only'] = letters_text.strip()
        except Exception as e:
            results['letters_only'] = f"Error: {str(e)}"
        
        # 6. Mixed content whitelist
        try:
            mixed_config = '--psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,:;!?()/-[] '
            mixed_text = pytesseract.image_to_string(image, lang=languages, config=mixed_config)
            results['mixed_content'] = mixed_text.strip()
        except Exception as e:
            results['mixed_content'] = f"Error: {str(e)}"
        return results
    
    def get_confidence_data(self, image, languages='eng'):
        """Get OCR confidence scores"""
        try:
            data = pytesseract.image_to_data(image, lang=languages, output_type=pytesseract.Output.DICT)
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            words = [word for word in data['text'] if word.strip()]
            
            return {
                'average_confidence': sum(confidences) / len(confidences) if confidences else 0,
                'min_confidence': min(confidences) if confidences else 0,
                'max_confidence': max(confidences) if confidences else 0,
                'total_words': len(words),
                'confident_words': len([c for c in confidences if c > 60])
            }
        except Exception as e:
            return {'error': str(e)}
    
    def select_best_result(self, ocr_results):
        """Select the best OCR result based on content analysis"""
        # Filter out error messages and empty results
        valid_results = {k: v for k, v in ocr_results.items() if v and not v.startswith('Error:') and len(v.strip()) > 0}
        
        if not valid_results:
            return {'method': 'none', 'text': '', 'score': 0}
        
        scored_results = []
        for method, text in valid_results.items():
            score = 0
            score += len(text.strip())
            has_letters = any(c.isalpha() for c in text)
            has_numbers = any(c.isdigit() for c in text)
            if has_letters and has_numbers:
                score += 100
            elif has_letters or has_numbers:
                score += 50
            if any(c in '.,;:!?()-[]' for c in text):
                score += 25
            if any(pattern in text.lower() for pattern in ['/', '-', ':', '2023', '2024', '2025']):
                score += 30
            
            # Penalty for too many special characters (likely noise)
            special_chars = sum(1 for c in text if not c.isalnum() and c not in ' .,;:!?()-[]/')
            if special_chars > len(text) * 0.3:  # More than 30% special chars
                score -= 50
            
            scored_results.append((score, method, text))
        best_score, best_method, best_text = max(scored_results, key=lambda x: x[0])
        return {'method': best_method, 'text': best_text, 'score': best_score}
    
    def process_single_image(self, image, languages='eng'):
        """Process a single image with multiple OCR configurations"""
        ocr_results = self.perform_multiple_ocr(image, languages)
        confidence_data = self.get_confidence_data(image, languages)
        best_result = self.select_best_result(ocr_results)
        valid_texts = [text for text in ocr_results.values() if text and not text.startswith('Error:') and len(text.strip()) > 0]
        
        return {
            'confidence_data': confidence_data,
            'best_result': best_result,
            'total_methods_tried': len(ocr_results),
            'successful_methods': len(valid_texts)
        }
    
    def process_pdf(self, pdf_path, output_path, dpi=300, lang='eng+ara'):
        """Process PDF file"""
        try:
            images = convert_from_path(pdf_path, dpi=dpi, poppler_path=self.poppler_path)
            print(f"Converted PDF to {len(images)} images")
        except Exception as e:
            print(f"Error converting PDF to images: {e}")
            return None
        
        pdf_text_pages = []
        try:
            src_pdf = fitz.open(pdf_path)
            for page_num in range(len(src_pdf)):
                pdf_text = src_pdf[page_num].get_text("text").strip()
                pdf_text_pages.append(pdf_text)
            src_pdf.close()
        except Exception as e:
            print(f"Could not extract PDF text: {e}")
            pdf_text_pages = [""] * len(images)
        

        results = {
            'document_info': {
                'source_file': pdf_path,
                'timestamp': datetime.datetime.now().isoformat(),
                'total_pages': len(images),
                'dpi': dpi,
                'ocr_languages': lang
            },
            'pages': []
        }
        
        for page_num, image in enumerate(images):
            print(f"Processing page {page_num + 1}/{len(images)}...")
            page_results = self.process_single_image(image, lang)
            page_data = {
                'page_number': page_num + 1,
                'original_pdf_text': pdf_text_pages[page_num] if page_num < len(pdf_text_pages) else "",
                'ocr_analysis': page_results
            }
            
            results['pages'].append(page_data)
            best = page_results['best_result']
            print(f"  Best method: {best['method']}")
            print(f"  Text length: {len(best['text'])} characters")
            print(f"  Successful methods: {page_results['successful_methods']}/{page_results['total_methods_tried']}")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        return results
    
    def process_image_file(self, image_path, output_path, lang='eng+ara'):
        """Process single image file"""
        try:
            image = Image.open(image_path)
            print(f"Loaded image: {image.size}")
        except Exception as e:
            print(f"Error loading image: {e}")
            return None
        
        image_results = self.process_single_image(image, lang)
        
        results = {
            'document_info': {
                'source_file': image_path,
                'timestamp': datetime.datetime.now().isoformat(),
                'image_size': image.size,
                'ocr_languages': lang
            },
            'ocr_analysis': image_results
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        return results

def main():
    input_file = 'C:\\Users\\user\\Desktop\\OCRTask\\LEASE AGREEMENT.pdf'
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f'C:\\Users\\user\\Desktop\\OCRTask\\ocrresult_{timestamp}.json'
    languages = 'eng+ara+urd' 
    processor = SimpleTextOCR(
        tesseract_path=r'D:\\TesseractOCR\\tesseract.exe',
        poppler_path=r"D:\\poppler\\poppler-24.08.0\\Library\\bin"
    )
    
    print(f"Processing: {input_file}")
    print(f"Languages: {languages}")
    print(f"Output: {output_file}")
    print("-" * 50)
    file_ext = os.path.splitext(input_file)[1].lower()
    
    if file_ext == '.pdf':
        results = processor.process_pdf(input_file, output_file, dpi=300, lang=languages)
        
        if results:
            print(f"\n{'='*50}")
            print("PDF PROCESSING COMPLETE")
            print(f"{'='*50}")
            print(f"Total pages: {len(results['pages'])}")
            
            for page in results['pages']:
                page_num = page['page_number']
                analysis = page['ocr_analysis']
                best = analysis['best_result']
                confidence = analysis['confidence_data']
                
                print(f"\nPage {page_num}:")
                print(f"  Best method: {best['method']}")
                print(f"  Success rate: {analysis['successful_methods']}/{analysis['total_methods_tried']}")
                
                if 'average_confidence' in confidence:
                    print(f"  Avg confidence: {confidence['average_confidence']:.1f}%")
                preview = best['text'][:150] + "..." if len(best['text']) > 150 else best['text']
                print(f"  Text preview: {repr(preview)}")
    
    elif file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']:
        results = processor.process_image_file(input_file, output_file, lang=languages)
        
        if results:
            analysis = results['ocr_analysis']  
            best = analysis['best_result']
            confidence = analysis['confidence_data']
            
            print(f"\n{'='*50}")
            print("IMAGE PROCESSING COMPLETE")
            print(f"{'='*50}")
            print(f"Best method: {best['method']}")
            print(f"Success rate: {analysis['successful_methods']}/{analysis['total_methods_tried']}")
            
            if 'average_confidence' in confidence:
                print(f"Average confidence: {confidence['average_confidence']:.1f}%")
    
    else:
        print("Error: Unsupported file format")
        print("Supported formats: PDF, JPG, JPEG, PNG, BMP, TIFF")

if __name__ == "__main__":
    main()