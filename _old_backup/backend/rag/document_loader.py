from pathlib import Path
from typing import Any
import pypdf
import docx

class DocumentLoader:
    @staticmethod
    def load_file(file_path: str | Path) -> list[dict[str, Any]]:
        """
        Loads PDF, DOCX, or TXT file and returns a list of pages:
        [{"page_number": 1, "text": "...", "source": filename}]
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Document not found at: {file_path}")

        ext = path.suffix.lower()
        if ext == ".pdf":
            return DocumentLoader._load_pdf(path)
        elif ext in [".docx", ".doc"]:
            return DocumentLoader._load_docx(path)
        else:
            return DocumentLoader._load_txt(path)

    @staticmethod
    def _load_pdf(path: Path) -> list[dict[str, Any]]:
        pages = []
        with open(path, "rb") as f:
            reader = pypdf.PdfReader(f)
            for idx, page in enumerate(reader.pages, start=1):
                text = page.extract_text() or ""
                clean_text = " ".join(text.split())
                if clean_text:
                    pages.append({
                        "page_number": idx,
                        "text": clean_text,
                        "source": path.name
                    })
        return pages

    @staticmethod
    def _load_docx(path: Path) -> list[dict[str, Any]]:
        doc = docx.Document(path)
        full_text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        return [{
            "page_number": 1,
            "text": full_text,
            "source": path.name
        }]

    @staticmethod
    def _load_txt(path: Path) -> list[dict[str, Any]]:
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(path, "r", encoding="latin-1") as f:
                content = f.read()

        return [{
            "page_number": 1,
            "text": content,
            "source": path.name
        }]
