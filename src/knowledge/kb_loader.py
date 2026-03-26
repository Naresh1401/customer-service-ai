"""
Knowledge Base Loader — Loads company knowledge base documents into ChromaDB
with topic/category-based chunking for RAG retrieval.
"""

import os
import glob
from pathlib import Path

import chromadb
from chromadb.config import Settings
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv

load_dotenv()

PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma_db")
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "customer_service_kb")
KB_DIR = Path("data/knowledge_base")

CATEGORY_MAP = {
    "faq": "Product FAQs",
    "billing": "Billing & Pricing",
    "troubleshooting": "Troubleshooting",
    "returns": "Returns & Refunds",
    "account": "Account Management",
}


def get_embeddings():
    """Initialize embedding model."""
    return HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
    )


def load_documents(kb_dir: Path = KB_DIR) -> list:
    """Load all .txt documents from the knowledge base directory."""
    documents = []
    txt_files = sorted(glob.glob(str(kb_dir / "*.txt")))

    if not txt_files:
        print(f"No .txt files found in {kb_dir}")
        return documents

    for filepath in txt_files:
        loader = TextLoader(filepath, encoding="utf-8")
        docs = loader.load()

        filename = Path(filepath).stem.lower()
        category = "General"
        for key, label in CATEGORY_MAP.items():
            if key in filename:
                category = label
                break

        for doc in docs:
            doc.metadata["category"] = category
            doc.metadata["source_file"] = Path(filepath).name

        documents.extend(docs)
        print(f"Loaded: {Path(filepath).name} → category: {category}")

    return documents


def chunk_documents(documents: list, chunk_size: int = 500, chunk_overlap: int = 50) -> list:
    """Split documents into chunks, preserving metadata."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(documents)
    print(f"Created {len(chunks)} chunks from {len(documents)} documents")
    return chunks


def load_into_chromadb(chunks: list, persist_dir: str = PERSIST_DIR) -> Chroma:
    """Load document chunks into ChromaDB with persistence."""
    embeddings = get_embeddings()

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=persist_dir,
    )

    print(f"Loaded {len(chunks)} chunks into ChromaDB at {persist_dir}")
    return vectorstore


def get_vectorstore(persist_dir: str = PERSIST_DIR) -> Chroma:
    """Get existing ChromaDB vectorstore."""
    embeddings = get_embeddings()
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=persist_dir,
    )


def query_kb(query: str, k: int = 4, category: str | None = None) -> list:
    """Query the knowledge base with optional category filter."""
    vectorstore = get_vectorstore()

    search_kwargs = {"k": k}
    if category:
        search_kwargs["filter"] = {"category": category}

    results = vectorstore.similarity_search(query, **search_kwargs)
    return results


def main():
    """Main entry point — load knowledge base into ChromaDB."""
    if not KB_DIR.exists():
        print(f"Knowledge base directory not found: {KB_DIR}")
        print("Run `python -m src.knowledge.sample_kb` first to generate sample data.")
        return

    documents = load_documents()
    if not documents:
        return

    chunks = chunk_documents(documents)
    load_into_chromadb(chunks)
    print("Knowledge base loaded successfully!")

    print("\nTest query: 'How do I reset my password?'")
    results = query_kb("How do I reset my password?", k=2)
    for i, doc in enumerate(results):
        print(f"\n--- Result {i + 1} [{doc.metadata.get('category', 'N/A')}] ---")
        print(doc.page_content[:200])


if __name__ == "__main__":
    main()
