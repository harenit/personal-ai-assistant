from typing import Any

class TextChunker:
    @staticmethod
    def chunk_pages(pages: list[dict[str, Any]], chunk_size: int = 600, overlap: int = 100) -> list[dict[str, Any]]:
        """
        Splits pages into overlapping chunks with metadata.
        Returns:
        [
            {
                "chunk_id": "doc.pdf_p1_c0",
                "text": "...",
                "source": "doc.pdf",
                "page_number": 1
            },
            ...
        ]
        """
        chunks = []
        for p in pages:
            text = p["text"]
            page_num = p["page_number"]
            source = p["source"]

            if len(text) <= chunk_size:
                chunks.append({
                    "chunk_id": f"{source}_p{page_num}_c0",
                    "text": text,
                    "source": source,
                    "page_number": page_num
                })
                continue

            start = 0
            chunk_idx = 0
            while start < len(text):
                end = start + chunk_size
                chunk_str = text[start:end]
                chunks.append({
                    "chunk_id": f"{source}_p{page_num}_c{chunk_idx}",
                    "text": chunk_str,
                    "source": source,
                    "page_number": page_num
                })
                chunk_idx += 1
                start += (chunk_size - overlap)

        return chunks
