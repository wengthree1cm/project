import fitz  # PyMuPDF

def extract_text_from_file(filepath):
    if filepath.endswith(".pdf"):
        doc = fitz.open(filepath)
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    elif filepath.endswith(".txt"):
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    else:
        return ""
