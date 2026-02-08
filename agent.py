def classify_query(query: str) -> str:
    q = query.lower()

    if "compare" in q or "difference" in q:
        return "comparison"
    if "which" in q or "has" in q or "what" in q:
        return "product_lookup"
    return "ambiguous"


def retrieval_k(query_type: str) -> int:
    if query_type == "comparison":
        return 8
    if query_type == "product_lookup":
        return 4
    return 6
