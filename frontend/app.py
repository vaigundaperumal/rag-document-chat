
import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="RAG Document Chat",
    page_icon="📚",
    layout="wide"
)

st.title("📚 RAG Document Chat")
st.caption("Upload your PDF and interact with your documents using AI.")

# Check backend connection
try:
    response = requests.get(f"{API_URL}/", timeout=5)
    response.raise_for_status()
    st.success("Backend connected")
except requests.exceptions.RequestException:
    st.error("Backend is not running. Start FastAPI first.")
    st.stop()

st.divider()

# Check document status
try:
    response = requests.get(
        f"{API_URL}/document/status",
        timeout=10
    )
    response.raise_for_status()
    status_data = response.json()
except requests.exceptions.RequestException as e:
    st.error(f"Could not get document status: {e}")
    st.stop()

# Display current document
if status_data["uploaded"]:
    document = status_data["document"]

    st.subheader("Current Document")

    col1, col2, col3 = st.columns(3)

    col1.metric("PDF Name", document["filename"])
    col2.metric("Total Pages", document["total_pages"])
    col3.metric("Total Chunks", document["total_chunks"])

    if st.button("Delete Current PDF"):
        try:
            response = requests.delete(
                f"{API_URL}/document",
                timeout=30
            )

            if response.ok:
                st.success("Document deleted!")
                st.rerun()
            else:
                st.error(response.text)

        except requests.exceptions.RequestException as e:
            st.error(f"Delete failed: {e}")

else:
    st.info("No PDF uploaded yet.")

st.divider()

# PDF upload
st.subheader("Upload a PDF")

uploaded_file = st.file_uploader(
    "Choose your PDF file",
    type=["pdf"]
)

if uploaded_file is not None:

    st.write(f"Selected file: **{uploaded_file.name}**")

    if st.button("Upload PDF", type="primary"):

        with st.spinner("Processing PDF... Please wait."):

            try:
                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        "application/pdf"
                    )
                }

                response = requests.post(
                    f"{API_URL}/upload",
                    files=files,
                    timeout=600
                )

                if response.ok:
                    result = response.json()
                    st.success(result["message"])
                    st.rerun()

                else:
                    try:
                        error = response.json().get(
                            "detail", response.text
                        )
                    except ValueError:
                        error = response.text

                    st.error(f"Upload failed: {error}")

            except requests.exceptions.RequestException as e:
                st.error(f"Connection error: {e}")


# -----------------------------
# AI Chat Section
# -----------------------------

if status_data["uploaded"]:

    st.divider()
    st.subheader("💬 Chat with your PDF")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display previous messages
    for message in st.session_state.messages:

        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            if message["role"] == "assistant":
                for source in message.get("sources", []):
                    st.caption(
                        f"📄 Source: {source['filename']} "
                        f"| Page: {source['page_number']}"
                    )

    # Chat input
    question = st.chat_input(
        "Ask anything about your uploaded PDF..."
    )

    if question:

        st.session_state.messages.append({
            "role": "user",
            "content": question
        })

        with st.spinner("AI is thinking..."):

            try:
                response = requests.post(
                    f"{API_URL}/chat",
                    json={"question": question},
                    timeout=180
                )

                response.raise_for_status()
                result = response.json()

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result["answer"],
                    "sources": result["sources"]
                })

                st.rerun()

            except requests.exceptions.RequestException as e:

                st.error(f"Chat request failed: {e}")

                st.session_state.messages.pop()
