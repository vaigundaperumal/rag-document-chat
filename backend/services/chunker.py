def create_chunks(pages, chunk_size=200, overlap=40):

    all_chunks = []

    step = chunk_size - overlap

    for page in pages:

        words = page["content"].split()

        for start in range(0, len(words), step):

            chunk_words = words[start:start + chunk_size]

            if not chunk_words:
                continue

            chunk_text = " ".join(chunk_words)

            all_chunks.append({
                "page_number": page["page_number"],
                "content": chunk_text
            })

            if start + chunk_size >= len(words):
                break

    return all_chunks