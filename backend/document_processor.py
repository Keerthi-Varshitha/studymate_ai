
from pathlib import Path
from pypdf import PdfReader
from docx import Document
from PIL import Image
import pytesseract


def extract_text(file_path):

    file_path = Path(file_path)
    extension = file_path.suffix.lower()

    if extension == ".pdf":

        reader = PdfReader(str(file_path))

        text = ""

        for page in reader.pages:
            text += page.extract_text() or ""

        return text

    elif extension == ".docx":

        document = Document(str(file_path))

        return "\n".join(
            paragraph.text
            for paragraph in document.paragraphs
        )

    elif extension == ".txt":

        return file_path.read_text(
            encoding="utf-8",
            errors="ignore"
        )

    elif extension in [".png", ".jpg", ".jpeg", ".webp"]:

        image = Image.open(file_path)

        return pytesseract.image_to_string(image)

    else:

        raise ValueError("Unsupported file format")


def split_text(text, chunk_size=500, overlap=100):

    words = text.split()

    chunks = []

    start = 0

    while start < len(words):

        end = start + chunk_size

        chunk = " ".join(words[start:end])

        if chunk.strip():
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks
