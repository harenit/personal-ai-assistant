"""Student document generation and PDF inspection module for AURA.

Uses python-docx to generate structured, professional Word documents (.docx)
and pypdf to extract, read, and summarize PDF assignments and lecture slides.
"""
from __future__ import annotations

import os
import re
from datetime import datetime
from pathlib import Path
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import pypdf

def _get_docs_dir() -> Path:
    env_dir = os.environ.get("AURA_DOCS_DIR")
    if env_dir:
        p = Path(env_dir)
        p.mkdir(parents=True, exist_ok=True)
        return p
    target = Path.home() / "Documents" / "AURA Documents"
    try:
        target.mkdir(parents=True, exist_ok=True)
        return target
    except OSError:
        fallback = Path.cwd() / "generated_documents"
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback


def _safe_name(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", name.strip()).strip("_")
    return cleaned[:70] or "document"


def create_word_document(title: str, topic: str = "", content: str | None = None) -> str:
    """Create a structured .docx file in Documents/AURA Documents."""
    title = title.strip() or "Student Document"
    topic = topic.strip() or title
    docs_dir = _get_docs_dir()
    filename = f"{_safe_name(title)}_{datetime.now():%Y%m%d_%H%M%S}.docx"
    target_path = docs_dir / filename

    doc = Document()

    # Style: Title
    h1 = doc.add_heading(title, level=0)
    h1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if h1.runs:
        h1.runs[0].font.name = "Segoe UI"
        h1.runs[0].font.size = Pt(26)
        h1.runs[0].font.bold = True
        h1.runs[0].font.color.rgb = RGBColor(0x38, 0xBD, 0xF8)  # AURA Cyan

    # Subtitle / Metadata
    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_sub = sub.add_run(f"Prepared by AURA Autonomous AI Companion  •  {datetime.now():%B %d, %Y}")
    run_sub.font.name = "Segoe UI"
    run_sub.font.size = Pt(10)
    run_sub.font.italic = True
    run_sub.font.color.rgb = RGBColor(0x94, 0xA3, 0xB8)

    doc.add_paragraph()  # Spacing

    if content and len(content.strip()) > 30:
        # User or LLM supplied structured text
        sections = content.strip().split("\n\n")
        for sec in sections:
            lines = sec.strip().split("\n")
            if lines:
                first = lines[0].strip().lstrip("#").strip()
                if len(lines) == 1 and len(first) < 60:
                    doc.add_heading(first, level=2)
                else:
                    if len(first) < 60 and len(lines) > 1:
                        doc.add_heading(first, level=2)
                        body_lines = lines[1:]
                    else:
                        body_lines = lines
                    for bl in body_lines:
                        bl_clean = bl.strip()
                        if bl_clean.startswith("- ") or bl_clean.startswith("* "):
                            doc.add_paragraph(bl_clean[2:], style="List Bullet")
                        else:
                            doc.add_paragraph(bl_clean)
    else:
        # Generate comprehensive academic report structure for the student
        doc.add_heading("1. Executive Summary", level=1)
        doc.add_paragraph(
            f"This academic report provides a systematic overview and critical analysis of {topic}. "
            "It outlines theoretical principles, practical applications, modern advancements, "
            "and implications for students and professionals in the domain."
        )

        doc.add_heading("2. Foundational Concepts", level=1)
        doc.add_paragraph(
            f"Understanding {topic} requires a solid grasp of underlying fundamentals, "
            "standard terminology, and core architectural components."
        )
        p_bullets = doc.add_paragraph(style="List Bullet")
        p_bullets.add_run(f"Key Principle: Primary mechanisms that govern {topic}.")
        p_bullets2 = doc.add_paragraph(style="List Bullet")
        p_bullets2.add_run(f"Core Advantages: Efficiency, scalability, and automated reasoning.")
        p_bullets3 = doc.add_paragraph(style="List Bullet")
        p_bullets3.add_run(f"Practical Relevance: Direct real-world integration in industry and research.")

        doc.add_heading("3. Implementation & Analysis", level=1)
        doc.add_paragraph(
            f"Real-world application of {topic} involves rigorous methodology, parameter tuning, "
            "and continuous feedback. Current state-of-the-art benchmarks illustrate significant productivity "
            "gains when paired with autonomous assisting workflows."
        )

        doc.add_heading("4. Key Takeaways & Recommendations", level=1)
        doc.add_paragraph(
            f"In conclusion, mastering {topic} offers substantial competitive advantages. "
            "Continuous hands-on exploration and empirical verification remain essential for lasting proficiency."
        )

    doc.save(str(target_path))
    return str(target_path)


def read_pdf_document(query_or_path: str) -> str:
    """Read and extract text from a local PDF file."""
    candidate_path: Path | None = None
    given = query_or_path.strip().strip("'\"")

    p = Path(given)
    if p.is_file() and p.suffix.lower() == ".pdf":
        candidate_path = p
    else:
        # Search common user directories for matching pdf
        search_dirs = [
            Path.home() / "Downloads",
            Path.home() / "Documents",
            Path.home() / "Desktop",
        ]
        target_name = p.name.lower()
        if not target_name.endswith(".pdf"):
            target_name += ".pdf"

        for d in search_dirs:
            if not d.is_dir():
                continue
            for item in d.glob("*.pdf"):
                if target_name in item.name.lower() or target_name.replace(".pdf", "") in item.name.lower():
                    candidate_path = item
                    break
            if candidate_path:
                break

    if not candidate_path or not candidate_path.is_file():
        return f"I couldn't locate a PDF matching '{query_or_path}' in your Downloads, Documents, or Desktop folders."

    try:
        reader = pypdf.PdfReader(str(candidate_path))
        num_pages = len(reader.pages)
        if num_pages == 0:
            return f"The PDF '{candidate_path.name}' is empty."

        extracted_text = []
        for i in range(min(num_pages, 8)):
            text = reader.pages[i].extract_text() or ""
            if text.strip():
                clean = re.sub(r"\s+", " ", text).strip()
                extracted_text.append(f"[Page {i+1}]: {clean[:600]}")

        if not extracted_text:
            return f"I opened '{candidate_path.name}' ({num_pages} pages), but could not extract selectable text (it may be a scanned image)."

        preview = "\n\n".join(extracted_text[:4])
        return f"Read '{candidate_path.name}' ({num_pages} total pages):\n\n{preview}"
    except Exception as exc:
        return f"Failed to read PDF '{candidate_path.name}': {exc}"
