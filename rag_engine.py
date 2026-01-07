"""
RAG Engine for Mevzuat-AI
Handles document processing, vector storage, and LLM interactions.
"""

import os
import tempfile
from typing import List, Dict, Any, Optional

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import Ollama
from langchain_core.documents import Document


# CONFIGURATION

OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "jarvis:latest"
CHROMA_PERSIST_DIR = "./chroma_db"
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K_RESULTS = 4

SYSTEM_PROMPT = """Sen Mevzuat-AI, Türk hukuku konusunda uzman profesyonel bir asistansın.
Görevin, kullanıcıların sorularını aşağıda verilen "Bağlam" (Context) içerisindeki bilgilere dayanarak analiz etmek ve yanıtlamaktır.

TALİMATLAR:
1. **Sentezle**: Bağlamdaki bilgileri kopyalayıp yapıştırmak yerine, soruyu yanıtlayacak şekilde birleştir ve yorumla.
2. **Akıcılık**: Cevabı bozuk cümlelerle değil, akıcı ve profesyonel bir Türkçe ile yaz. Robotik dilden kaçın.
3. **Doğruluk**: Asla bağlamda olmayan bir bilgi, kanun maddesi veya hüküm uydurma.
4. **Yapı**: Cevabı şu formatta ver:
   - **Özet**: Cevabın 1-2 cümlelik net özeti.
   - **Detaylar**: Varsa, maddeler halinde detaylı açıklamalar.

Eğer sorunun cevabı bağlamda kesinlikle yoksa, sadece "Yüklenen belgelerde bu konu hakkında bilgi bulunmamaktadır." yaz.

Bağlam:
{context}

Soru: {question}

Yanıt:"""


# SINGLETON INSTANCES

_embeddings = None
_llm = None


def get_embeddings():
    """Get or create embeddings instance."""
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
    return _embeddings


def get_llm():
    """Get or create LLM instance."""
    global _llm
    if _llm is None:
        _llm = Ollama(
            base_url=OLLAMA_BASE_URL,
            model=OLLAMA_MODEL,
            temperature=0.1,
            num_ctx=4096,
        )
    return _llm


def get_vector_store() -> Optional[Chroma]:
    """Get ChromaDB vector store if exists."""
    if os.path.exists(CHROMA_PERSIST_DIR):
        return Chroma(
            persist_directory=CHROMA_PERSIST_DIR, 
            embedding_function=get_embeddings()
        )
    return None


# DOCUMENT PROCESSING

def process_pdf(pdf_path: str, original_filename: str) -> List[Document]:
    """Process a PDF file and return documents."""
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    
    for doc in documents:
        doc.metadata['source_file'] = original_filename
    
    return documents


def chunk_documents(documents: List[Document]) -> List[Document]:
    """Split documents into chunks."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    return text_splitter.split_documents(documents)


def ingest_documents(pdf_files: List[Dict]) -> int:
    """
    Ingest PDF files into vector store.
    
    Args:
        pdf_files: List of dicts with 'path' and 'filename' keys
        
    Returns:
        Number of chunks created
    """
    all_documents = []
    
    for pdf_info in pdf_files:
        docs = process_pdf(pdf_info['path'], pdf_info['filename'])
        all_documents.extend(docs)
    
    if not all_documents:
        return 0
    
    chunks = chunk_documents(all_documents)
    
    # Clear existing store
    if os.path.exists(CHROMA_PERSIST_DIR):
        import shutil
        shutil.rmtree(CHROMA_PERSIST_DIR)
    
    # Create new vector store
    Chroma.from_documents(
        documents=chunks,
        embedding=get_embeddings(),
        persist_directory=CHROMA_PERSIST_DIR
    )
    
    return len(chunks)


# RAG QUERY

def query_rag(question: str) -> Dict[str, Any]:
    """
    Execute RAG query and return answer with sources.
    
    Args:
        question: User's question
        
    Returns:
        Dict with 'answer' and 'sources' keys
    """
    vector_store = get_vector_store()
    
    if vector_store is None:
        return {
            "answer": "Henüz analiz edilmiş belge bulunmuyor. Lütfen önce PDF belgelerinizi yükleyin ve analiz edin.",
            "sources": []
        }
    
    # Retrieve relevant documents
    retriever = vector_store.as_retriever(
        search_type="similarity", 
        search_kwargs={"k": TOP_K_RESULTS}
    )
    relevant_docs = retriever.invoke(question)
    
    if not relevant_docs:
        return {
            "answer": "Bu soru ile ilgili belgelerde bilgi bulunamadı.",
            "sources": []
        }
    
    # Build context and prompt
    context = "\n\n---\n\n".join([doc.page_content for doc in relevant_docs])
    prompt = SYSTEM_PROMPT.format(context=context, question=question)
    
    # Get LLM response
    try:
        llm = get_llm()
        answer = llm.invoke(prompt)
    except Exception as e:
        error_msg = str(e)
        if "memory" in error_msg.lower():
            return {
                "answer": f"Model bellek hatası. Sisteminizde yeterli RAM yok. Lütfen daha küçük bir model kullanın.",
                "sources": []
            }
        return {
            "answer": f"LLM yanıt veremedi. Ollama'nın çalıştığından emin olun. Hata: {error_msg}",
            "sources": []
        }
    
    # Format sources
    sources = []
    for i, doc in enumerate(relevant_docs, 1):
        page = doc.metadata.get('page', 0)
        page_num = page + 1 if isinstance(page, int) else page
        sources.append({
            "id": i,
            "page": page_num,
            "file": doc.metadata.get('source_file', 'Bilinmeyen'),
            "preview": doc.page_content[:250] + "..." if len(doc.page_content) > 250 else doc.page_content
        })
    
    return {
        "answer": answer,
        "sources": sources
    }


def get_system_info() -> Dict[str, Any]:
    """Get system configuration info."""
    return {
        "model": OLLAMA_MODEL.split(":")[0],
        "chunk_size": CHUNK_SIZE,
        "top_k": TOP_K_RESULTS,
        "embedding_model": EMBEDDING_MODEL.split("/")[-1]
    }
