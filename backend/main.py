
import uuid
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel

from services.pdf_reader import extract_text
from services.chunker import create_chunks
from services.embeddings import generate_embeddings
from services.retriever import retrieve_chunks
from services.prompt_builder import build_prompt
from services.llm import generate_answer
from services.vector_store import (
    store_chunks,
    wait_until_stored,
    delete_namespace_documents
)


# -----------------------------
# Application configuration
# -----------------------------

app = FastAPI(
    title="RAG Document Chat API",
    description="Upload PDFs and ask questions using AI",
    version="1.0.0"
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

MAX_FILE_SIZE = 10 * 1024 * 1024

# Stores the currently active PDF
active_document = None


# -----------------------------
# Request and response models
# -----------------------------

class ChatRequest(BaseModel):
    question: str


class Source(BaseModel):
    page_number: int
    filename: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]


# -----------------------------
# Home endpoint
# -----------------------------

@app.get("/")
def home():

    return {
        "message": "RAG Document Chat API is running"
    }


# -----------------------------
# PDF upload endpoint
# -----------------------------

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    global active_document

    if not file.filename or Path(file.filename).suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    file_content = await file.read(MAX_FILE_SIZE + 1)

    if not file_content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded PDF is empty."
        )

    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="PDF size must not exceed 10 MB."
        )

    if not file_content.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=400,
            detail="Invalid PDF file."
        )

    document_id = str(uuid.uuid4())
    namespace = f"rag-{document_id}"

    filename = Path(file.filename).name
    file_path = UPLOAD_DIR / f"{document_id}.pdf"

    new_document_stored = False

    try:

        # Save PDF
        with open(file_path, "wb") as f:
            f.write(file_content)

        # Extract text
        pages = extract_text(str(file_path))

        if not pages or not any(
            page["content"].strip() for page in pages
        ):
            raise HTTPException(
                status_code=400,
                detail="No readable text found in this PDF."
            )

        # Create chunks
        chunks = create_chunks(pages)

        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="Could not create document chunks."
            )

        # Generate embeddings
        embeddings = generate_embeddings(chunks)

        # Store in a new Pinecone namespace
        store_chunks(
            chunks,
            embeddings,
            filename,
            namespace
        )

        # Verify Pinecone storage
        stored = wait_until_stored(namespace, chunks)

        if not stored:
            raise HTTPException(
                status_code=500,
                detail="Pinecone storage verification failed."
            )

        new_document_stored = True

        # Save previous document information
        old_document = active_document

        # Activate the new document
        active_document = {
            "document_id": document_id,
            "filename": filename,
            "namespace": namespace,
            "total_pages": len(pages),
            "total_chunks": len(chunks)
        }

        # Remove previous document
        if old_document:

            try:
                delete_namespace_documents(
                    old_document["namespace"]
                )

                old_file = (
                    UPLOAD_DIR /
                    f"{old_document['document_id']}.pdf"
                )

                if old_file.exists():
                    old_file.unlink()

            except Exception as cleanup_error:
                # New document remains active.
                # Old namespace is no longer used for retrieval.
                print("Old document cleanup failed:", cleanup_error)

        return {
            "message": "PDF uploaded successfully!",
            "document": active_document
        }

    except HTTPException:
        raise

    except Exception as e:

        # Clean up failed upload
        if new_document_stored:
            try:
                delete_namespace_documents(namespace)
            except Exception:
                pass

        raise HTTPException(
            status_code=500,
            detail=f"PDF processing failed: {str(e)}"
        )

    finally:

        await file.close()

        # Remove temporary file if this upload did not become active
        if (
            file_path.exists()
            and (
                active_document is None
                or active_document["document_id"] != document_id
            )
        ):
            file_path.unlink()


# -----------------------------
# Document status endpoint
# -----------------------------

@app.get("/document/status")
def document_status():

    if active_document is None:
        return {
            "uploaded": False,
            "message": "No PDF uploaded yet."
        }

    return {
        "uploaded": True,
        "document": active_document
    }


# -----------------------------
# Chat endpoint
# -----------------------------

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    if active_document is None:
        raise HTTPException(
            status_code=400,
            detail="Please upload a PDF before asking questions."
        )

    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    # Retrieve chunks from active PDF only
    chunks = retrieve_chunks(
        request.question,
        active_document["namespace"]
    )

    if not chunks:
        return ChatResponse(
            answer="I couldn't find the answer in the uploaded document.",
            sources=[]
        )

    # Build context-aware prompt
    prompt = build_prompt(
        request.question,
        chunks
    )

    # Generate answer using Ollama
    answer = generate_answer(prompt)

    # Prepare source information
    sources = [
        Source(
            page_number=chunk["page_number"],
            filename=chunk["filename"]
        )
        for chunk in chunks
    ]

    return ChatResponse(
        answer=answer,
        sources=sources
    )


# -----------------------------
# Delete document endpoint
# -----------------------------

@app.delete("/document")
def delete_document():

    global active_document

    if active_document is None:
        return {
            "message": "No active document to delete."
        }

    document = active_document

    # Delete Pinecone records
    delete_namespace_documents(document["namespace"])

    # Delete local PDF
    file_path = (
        UPLOAD_DIR /
        f"{document['document_id']}.pdf"
    )

    if file_path.exists():
        file_path.unlink()

    active_document = None

    return {
        "message": "Document deleted successfully."
    }
