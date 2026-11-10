from services.pdf_reader import extract_text
from services.chunker import create_chunks

pdf_path = "uploads/machine_learning_5_pages.pdf"

# Extract PDF text
pages = extract_text(pdf_path)

print("Total pages:", len(pages))

# Create chunks
chunks = create_chunks(
    pages,
    chunk_size=200,
    overlap=40
)

print("Total chunks:", len(chunks))

# Display chunks
for i, chunk in enumerate(chunks):

    print("\nCHUNK:", i + 1)
    print("PAGE:", chunk["page_number"])
    print(chunk["content"])