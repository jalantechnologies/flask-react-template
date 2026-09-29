def page_count(total_items: int, page_size: int) -> int:
    if page_size <= 0:
        raise ValueError("page_size must be positive")
    return -(-total_items // page_size)
