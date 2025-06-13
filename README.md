# 🧠 VersaOCR - Multi-Strategy Intelligent OCR Processor

**VersaOCR** is a powerful Python-based OCR tool designed to intelligently extract text from PDFs and images using multiple Tesseract configurations. It selects the best OCR result per page through scoring and confidence metrics, making it ideal for processing multilingual, scanned, or noisy documents.

---

## 🚀 Features

- ✅ Supports both **PDF** and **Image** file formats  
- 🔁 Applies **multiple Tesseract OCR modes** (PSMs, OEMs, whitelists)  
- 🧠 Automatically selects the **best OCR output** based on content quality  
- 🌐 Multilingual OCR (supports `eng`, `ara`, `urd`, etc.)  
- 📊 Generates **detailed confidence metrics** for each page  
- 📝 Extracts embedded PDF text using `PyMuPDF` (when available)  
- 📤 Outputs clean JSON reports for downstream analysis  

---

## 📂 Example Output

The output is a structured `.json` file that includes:

- Best method and extracted text  
- OCR confidence data (average, min, max)  
- Number of successful methods  
- Original embedded PDF text (if available)  

---

## 📦 Dependencies

Install the required packages:

```bash
pip install pytesseract pdf2image Pillow PyMuPDF
```

Also ensure:

- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) is installed and accessible via system PATH  
- [Poppler](http://blog.alivate.com.au/poppler-windows/) is installed for PDF to image conversion (especially on Windows)

---

## 🧪 How It Works

For each page:

1. The PDF is converted to high-resolution images (via `pdf2image`)
2. Multiple OCR passes are run using Tesseract with different:
   - Page segmentation modes (`--psm`)
   - OCR engines (`--oem`)
   - Character whitelists
3. Confidence scores are computed using `image_to_data()`
4. A scoring system ranks each result to select the **best** OCR text

---

## 🖼️ Usage

### 🔹 Process a PDF

```bash
python your_script.py
```

Edit `main()` with the correct `input_file` or call `processor.process_pdf()` directly.

### 🔹 Process a Single Image

```python
processor.process_image_file("path_to_image.jpg", "output.json", lang="eng+ara")
```

---

## 🧠 Output Sample (JSON)

```json
{
  "document_info": {
    "source_file": "LEASE AGREEMENT.pdf",
    "timestamp": "2025-06-12T15:00:00",
    "total_pages": 3,
    "dpi": 300,
    "ocr_languages": "eng+ara+urd"
  },
  "pages": [
    {
      "page_number": 1,
      "original_pdf_text": "Agreement made this day...",
      "ocr_analysis": {
        "confidence_data": {
          "average_confidence": 86.4,
          "min_confidence": 65,
          "max_confidence": 97,
          "total_words": 122,
          "confident_words": 109
        },
        "best_result": {
          "method": "lstm_engine",
          "text": "This Lease Agreement is made...",
          "score": 213
        },
        "total_methods_tried": 9,
        "successful_methods": 8
      }
    }
  ]
}
```

---

## 🧰 File Structure

```
📁 OCRProject
├── your_script.py
├── README.md
├── output/
│   └── ocrresult_YYYYMMDD_HHMMSS.json
└── input/
    └── document.pdf
```

---

## 🔧 Configuration

Edit the following in `main()`:

```python
input_file = 'path\to\your\document.pdf'
languages = 'eng+ara+urd'
```

Set Tesseract executable and language data path:

```python
pytesseract.pytesseract.tesseract_cmd = r'D:\TesseractOCR\tesseract.exe'
os.environ['TESSDATA_PREFIX'] = r'D:\TesseractOCR\tessdata'
```

---

## 📈 Future Improvements (Optional)

- PDF postprocessing with layout preservation (e.g., bounding boxes)  
- Integration with cloud OCR APIs for fallback  
- GUI-based uploader or dashboard (Streamlit, Gradio)  
- Add CSV/Text output support alongside JSON  

---

## 📃 License

This project is released under the [MIT License](https://opensource.org/licenses/MIT).

---

## 🙌 Acknowledgements

- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)  
- [Poppler Utils](https://poppler.freedesktop.org/)  
- [PyMuPDF](https://github.com/pymupdf/PyMuPDF)

---

> Built with 💡 and Python to make text extraction smarter and more reliable.
