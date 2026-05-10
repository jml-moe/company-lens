import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from pydantic import BaseModel

from app.core.llm import ensure_openrouter_configured
from app.core.settings import settings

COLLECTION_NAME = "company_research"
CHUNK_SIZE = 2000
CHUNK_OVERLAP = 300


class StoredChunk(BaseModel):
    content: str
    chromadb_id: str
    chunk_index: int


class SearchResult(BaseModel):
    content: str
    metadata: dict
    distance: float | None


def build_research_document(
    *,
    name: str,
    industry: str,
    overview: str,
    products: str,
    competitors: str,
    recent_news: str,
) -> str:
    sections = [f"# {name}\n**Industry:** {industry}\n", overview]
    if products:
        sections.append(f"## Products and Services (extracted)\n{products}")
    if competitors:
        sections.append(f"## Competitive Landscape (extracted)\n{competitors}")
    if recent_news:
        sections.append(f"## Recent Developments (extracted)\n{recent_news}")
    return "\n\n".join(sections)


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    normalized = " ".join(text.split())
    if not normalized:
        return []

    chunks = []
    start = 0
    while start < len(normalized):
        end = min(start + chunk_size, len(normalized))
        chunks.append(normalized[start:end])
        if end == len(normalized):
            break
        start = max(end - overlap, 0)
    return chunks


def get_embedding_function() -> OpenAIEmbeddingFunction:
    ensure_openrouter_configured()
    return OpenAIEmbeddingFunction(
        api_key=settings.OPENROUTER_API_KEY,
        api_base=settings.OPENROUTER_BASE_URL,
        model_name=settings.EMBEDDING_MODEL,
    )


def get_chroma_client():
    return chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)


def get_collection():
    return get_chroma_client().get_or_create_collection(
        name=COLLECTION_NAME, embedding_function=get_embedding_function()
    )


def store_chunks(company_id: str, text: str) -> list[StoredChunk]:
    chunks = chunk_text(text)
    if not chunks:
        return []
    ids = [f"{company_id}:{i}" for i in range(len(chunks))]
    metadatas = [{"company_id": company_id, "chunk_index": i} for i in range(len(chunks))]
    get_collection().upsert(ids=ids, documents=chunks, metadatas=metadatas)
    return [
        StoredChunk(content=c, chromadb_id=cid, chunk_index=i)
        for i, (c, cid) in enumerate(zip(chunks, ids, strict=True))
    ]


def search(query: str, company_id: str, top_k: int = 5) -> list[SearchResult]:
    results = get_collection().query(
        query_texts=[query], n_results=top_k, where={"company_id": company_id}
    )
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0] if results.get("distances") else []
    padded = list(distances) + [None] * (len(documents) - len(distances))
    return [
        SearchResult(content=d, metadata=m or {}, distance=dist)
        for d, m, dist in zip(documents, metadatas, padded, strict=False)
    ]


def delete_company_chunks(company_id: str) -> None:
    try:
        collection = get_chroma_client().get_collection(name=COLLECTION_NAME)
    except ValueError:
        return
    ids = collection.get(where={"company_id": company_id}).get("ids", [])
    if ids:
        collection.delete(ids=ids)
