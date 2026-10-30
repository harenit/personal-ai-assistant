from pathlib import Path
from backend.config.settings import settings
from backend.rag.vector_store import vector_store

def test_rag_pipeline():
    # Create a test document
    test_doc_path = settings.DOCUMENTS_DIR / "sample_ai_notes.txt"
    with open(test_doc_path, "w", encoding="utf-8") as f:
        f.write("""
Artificial Intelligence Exam Study Guide:
Heuristic search algorithms such as A* evaluate nodes using f(n) = g(n) + h(n).
An admissible heuristic never overestimates the true remaining distance to the goal.
In multi-layer perceptron neural networks, backpropagation applies the multivariate chain rule to calculate weight gradients.
Red-Black trees ensure O(log n) worst-case time by enforcing tree balancing invariants.
""")

    chunks_indexed = vector_store.add_document("sample_doc_1", test_doc_path)
    assert chunks_indexed >= 1

    # Search for heuristic search
    results = vector_store.search("admissible heuristic A*", top_k=2)
    assert len(results) > 0
    top = results[0]
    assert "admissible" in top["text"].lower() or "heuristic" in top["text"].lower()
    assert top["source"] == "sample_ai_notes.txt"
    assert top["page_number"] == 1
