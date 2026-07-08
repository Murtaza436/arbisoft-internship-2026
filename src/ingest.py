import os
import chromadb
from pypdf import PdfReader


def load_pdfs(pdf_dir):
    """Load all PDFs from a directory and return list of (filename, text)."""
    documents = []
    for filename in os.listdir(pdf_dir):
        if filename.endswith('.pdf'):
            path = os.path.join(pdf_dir, filename)
            reader = PdfReader(path)
            text = ''
            for page in reader.pages:
                text += page.extract_text() or ''
            documents.append((filename, text))
            print(f'Loaded: {filename} ({len(reader.pages)} pages)')
    return documents


def chunk_text(text, chunk_size=500, overlap=50):
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk)
        start = end - overlap
    return chunks


def ingest_documents(pdf_dir, collection_name='week3_docs'):
    """Load PDFs, chunk them, and store in ChromaDB."""
    client = chromadb.PersistentClient(path='./chroma_db')

    try:
        client.delete_collection(collection_name)
    except Exception:
        pass

    collection = client.create_collection(collection_name)
    documents = load_pdfs(pdf_dir)

    all_chunks = []
    all_ids = []
    all_metadata = []

    chunk_id = 0
    for filename, text in documents:
        chunks = chunk_text(text)
        for chunk in chunks:
            all_chunks.append(chunk)
            all_ids.append(f'chunk_{chunk_id}')
            all_metadata.append({'source': filename})
            chunk_id += 1

    collection.add(
        documents=all_chunks,
        ids=all_ids,
        metadatas=all_metadata
    )

    print(f'Stored {len(all_chunks)} chunks in ChromaDB')
    return collection
