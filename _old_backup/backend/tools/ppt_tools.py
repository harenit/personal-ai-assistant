import os
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor

from backend.tools.base import BaseTool
from backend.permissions.models import RiskLevel
from backend.config.settings import settings
from backend.database.connection import SessionLocal
from backend.database.models import GeneratedFile

class GeneratePresentationTool(BaseTool):
    name = "generate_presentation"
    description = "Generate a real Microsoft PowerPoint (.pptx) presentation with custom slides, formatted sections, bullet points, and speaker notes on any requested academic or technical topic."
    risk_level = RiskLevel.LOW_RISK
    parameters = {
        "type": "object",
        "properties": {
            "topic": {
                "type": "string",
                "description": "Topic or title of the presentation (e.g. 'Artificial Intelligence', 'Binary Trees', 'Machine Learning Seminar')"
            },
            "slide_count": {
                "type": "integer",
                "description": "Number of slides to generate (default 8 to 10)",
                "default": 10
            },
            "audience": {
                "type": "string",
                "description": "Target audience (e.g. 'College Students', 'Professor / Seminar', 'Beginners')",
                "default": "College Students"
            },
            "key_points": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional specific subtopics or key points to include"
            }
        },
        "required": ["topic"]
    }

    def execute(self, topic: str, slide_count: int = 10, audience: str = "College Students", key_points: Optional[list[str]] = None, **kwargs) -> dict[str, Any]:
        try:
            try:
                slide_count = int(slide_count)
            except (ValueError, TypeError):
                slide_count = 10
            slide_count = max(3, min(slide_count, 20))
            prs = Presentation()
            # 16:9 widescreen layout
            prs.slide_width = Inches(13.333)
            prs.slide_height = Inches(7.5)
            blank_slide_layout = prs.slide_layouts[6]

            # Color scheme: Modern Navy & Cyan / Indigo
            PRIMARY_COLOR = RGBColor(15, 23, 42)      # Deep Slate/Navy #0F172A
            ACCENT_COLOR = RGBColor(56, 189, 248)     # Sky Blue #38BDF8
            TEXT_DARK = RGBColor(30, 41, 59)          # Dark text #1E293B
            TEXT_LIGHT = RGBColor(248, 250, 252)     # Off-white #F8FAFC
            MUTED_COLOR = RGBColor(100, 116, 139)     # Slate #64748B

            # Outline generation based on topic
            slides_data = self._generate_slide_outline(topic, slide_count, audience, key_points)

            # Slide 1: Title Slide
            title_slide = prs.slides.add_slide(blank_slide_layout)
            self._set_slide_background(title_slide, PRIMARY_COLOR)

            tx_box = title_slide.shapes.add_textbox(Inches(1.5), Inches(2.0), Inches(10.33), Inches(3.0))
            tf = tx_box.text_frame
            tf.word_wrap = True

            p1 = tf.paragraphs[0]
            p1.text = topic.upper()
            p1.font.bold = True
            p1.font.size = Pt(44)
            p1.font.color.rgb = ACCENT_COLOR
            p1.alignment = PP_ALIGN.CENTER

            p2 = tf.add_paragraph()
            p2.text = f"Comprehensive Academic Overview & Technical Analysis\nAudience: {audience}"
            p2.font.size = Pt(22)
            p2.font.color.rgb = TEXT_LIGHT
            p2.alignment = PP_ALIGN.CENTER

            p3 = tf.add_paragraph()
            p3.text = f"\nPrepared by JARVIS AI • Student: Alex Rivers • {datetime.now().strftime('%B %Y')}"
            p3.font.size = Pt(14)
            p3.font.color.rgb = MUTED_COLOR
            p3.alignment = PP_ALIGN.CENTER

            # Speaker note for title slide
            notes = title_slide.notes_slide.notes_text_frame
            notes.text = f"Welcome everyone. Today we are presenting on {topic}. This presentation covers fundamental principles, modern architecture, real-world case studies, and future outlook."

            # Subsequent content slides
            for idx, s_info in enumerate(slides_data[1:], start=2):
                slide = prs.slides.add_slide(blank_slide_layout)
                
                # Header Bar
                header_box = slide.shapes.add_textbox(Inches(1.0), Inches(0.6), Inches(11.33), Inches(1.2))
                htf = header_box.text_frame
                htf.word_wrap = True
                hp = htf.paragraphs[0]
                hp.text = s_info["title"]
                hp.font.bold = True
                hp.font.size = Pt(28)
                hp.font.color.rgb = PRIMARY_COLOR

                # Subtitle/category
                hp2 = htf.add_paragraph()
                hp2.text = f"Part {idx} of {slide_count} • {topic}"
                hp2.font.size = Pt(12)
                hp2.font.color.rgb = MUTED_COLOR

                # Content Box
                content_box = slide.shapes.add_textbox(Inches(1.2), Inches(2.0), Inches(10.9), Inches(4.8))
                ctf = content_box.text_frame
                ctf.word_wrap = True

                for b_idx, bullet in enumerate(s_info["bullets"]):
                    bp = ctf.paragraphs[0] if b_idx == 0 else ctf.add_paragraph()
                    bp.text = f"•  {bullet}"
                    bp.font.size = Pt(18)
                    bp.font.color.rgb = TEXT_DARK
                    bp.space_after = Pt(14)

                # Speaker notes
                slide_notes = slide.notes_slide.notes_text_frame
                slide_notes.text = s_info.get("speaker_notes", f"Speaker discussion points for {s_info['title']}.")

            # Save presentation
            safe_topic = re.sub(r'[^\w\s-]', '', topic).strip().replace(" ", "_")
            file_name = f"{safe_topic}_{uuid.uuid4().hex[:6]}.pptx"
            file_path = settings.PRESENTATIONS_DIR / file_name
            prs.save(str(file_path))

            # Record in DB
            db = SessionLocal()
            try:
                gen_file = GeneratedFile(
                    file_name=file_name,
                    file_type="pptx",
                    file_path=str(file_path),
                    title=f"{topic} Presentation",
                    description=f"{slide_count}-slide presentation on {topic} for {audience}."
                )
                db.add(gen_file)
                db.commit()
            finally:
                db.close()

            return {
                "success": True,
                "action": "generate_presentation",
                "topic": topic,
                "slide_count": slide_count,
                "file_name": file_name,
                "file_path": str(file_path),
                "download_url": f"/generated/presentations/{file_name}",
                "message": f"Successfully generated '{file_name}' ({slide_count} slides) in presentations folder."
            }

        except Exception as e:
            return {
                "success": False,
                "action": "generate_presentation",
                "topic": topic,
                "message": f"Failed to generate presentation: {str(e)}"
            }

    def _set_slide_background(self, slide, color: RGBColor):
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = color

    def _generate_slide_outline(self, topic: str, count: int, audience: str, key_points: Optional[list[str]]) -> list[dict[str, Any]]:
        # Comprehensive outline templates for technical and academic presentations
        base_sections = [
            {
                "title": f"Introduction & Core Motivation",
                "bullets": [
                    f"Understanding the fundamental importance of {topic} in modern computing.",
                    "Historical evolution from foundational theory to state-of-the-art implementations.",
                    "Why this domain matters for industry practitioners, researchers, and students."
                ],
                "speaker_notes": f"Set the stage by highlighting why {topic} is critical today."
            },
            {
                "title": f"Theoretical Foundations & Key Principles",
                "bullets": [
                    "Mathematical models, formal definitions, and core abstractions.",
                    "Algorithmic complexity, state-space exploration, and trade-offs.",
                    "Core governing equations, structural invariant assumptions, and paradigms."
                ],
                "speaker_notes": "Emphasize conceptual clarity and the mathematical framework."
            },
            {
                "title": f"System Architecture & Components",
                "bullets": [
                    "High-level structural breakdown and modular component interaction.",
                    "Data ingestion, representation pipelines, and state transitions.",
                    "Integration interfaces with adjacent infrastructure and computing hardware."
                ],
                "speaker_notes": "Walk through the architecture diagram and data flow."
            },
            {
                "title": f"Key Algorithms & Methodologies",
                "bullets": [
                    "Primary operational algorithms and optimization techniques.",
                    "Heuristics, loss minimization, and convergence guarantees.",
                    "Handling edge cases, scaling bottlenecks, and computational constraints."
                ],
                "speaker_notes": "Highlight algorithmic efficiency and practical considerations."
            },
            {
                "title": f"Practical Implementation & Tooling",
                "bullets": [
                    "Popular frameworks, libraries, and open-source ecosystems.",
                    "Best practices for production deployment, profiling, and benchmarking.",
                    "Code design patterns and testing strategies for robustness."
                ],
                "speaker_notes": "Discuss real code and engineering practices."
            },
            {
                "title": f"Comparative Analysis & Benchmarks",
                "bullets": [
                    "Empirical performance comparison against alternative methodologies.",
                    "Latency, throughput, memory footprint, and scalability metrics.",
                    "When to adopt this approach vs. simpler classical alternatives."
                ],
                "speaker_notes": "Present benchmark data and decision criteria."
            },
            {
                "title": f"Case Studies & Industry Applications",
                "bullets": [
                    "Deployment at scale: healthcare, autonomous systems, finance, and cloud.",
                    "Lessons learned from real-world production incidents and scale hurdles.",
                    "Measurable impact on efficiency, accuracy, and operational throughput."
                ],
                "speaker_notes": "Ground the theory in tangible industry success stories."
            },
            {
                "title": f"Challenges, Limitations & Ethical Dimensions",
                "bullets": [
                    "Open research problems and current computational boundaries.",
                    "Data bias, transparency, security vulnerabilities, and governance.",
                    "Mitigation strategies and responsible engineering guidelines."
                ],
                "speaker_notes": "Critically analyze failure modes and ethical responsibilities."
            },
            {
                "title": f"Future Trends & Emerging Horizons",
                "bullets": [
                    "Next-generation paradigms currently emerging from top research labs.",
                    "Hardware acceleration, neuromorphic architectures, and distributed scaling.",
                    "Anticipated breakthroughs over the next 3 to 5 years."
                ],
                "speaker_notes": "Inspire the audience with upcoming innovations."
            },
            {
                "title": f"Summary, Conclusion & References",
                "bullets": [
                    f"Recap of core takeaways and foundational concepts in {topic}.",
                    "Recommended papers, standard textbooks, and official documentation for deeper study.",
                    "Q&A Session: Open discussion and questions from the floor."
                ],
                "speaker_notes": "Summarize main points and transition to audience Q&A."
            }
        ]

        if key_points and len(key_points) > 0:
            for i, pt in enumerate(key_points[:count-1]):
                if i < len(base_sections):
                    base_sections[i]["bullets"].insert(0, f"Focus Point: {pt}")

        # Ensure exact count (including title)
        needed_content_slides = count - 1
        return [{"title": topic}] + base_sections[:needed_content_slides]
