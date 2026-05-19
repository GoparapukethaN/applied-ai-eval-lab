from time import perf_counter

from fastapi import APIRouter

from app.core.config import get_settings
from app.core.errors import bad_request
from app.documents.chunking import chunk_documents
from app.documents.samples import load_sample_documents
from app.evaluation.scoring import DEFAULT_EVAL_EXAMPLES, summarize_evaluation
from app.generation.grounded import build_grounded_answer
from app.models.schemas import (
    DocumentSummary,
    EvaluationRequest,
    EvaluationSummary,
    HealthResponse,
    IndexRequest,
    IndexResponse,
    QueryRequest,
    QueryResponse,
    SourceDocument,
)
from app.retrieval.vector_store import InMemoryVectorStore

router = APIRouter()
VECTOR_STORE = InMemoryVectorStore()
INDEXED_DOCUMENTS: dict[str, SourceDocument] = {}


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(status="ok", service=settings.app_name)


@router.get("/documents/samples", response_model=list[DocumentSummary])
def sample_documents() -> list[DocumentSummary]:
    return [
        DocumentSummary(
            id=document.id,
            title=document.title,
            kind=document.kind,
            char_count=len(document.text),
            metadata=document.metadata,
        )
        for document in load_sample_documents()
    ]


@router.post("/documents/index", response_model=IndexResponse)
def index_documents(request: IndexRequest) -> IndexResponse:
    settings = get_settings()
    sample_documents_by_id = {document.id: document for document in load_sample_documents()}
    selected_documents: list[SourceDocument] = []

    for document_id in request.document_ids:
        document = sample_documents_by_id.get(document_id)
        if document is None:
            raise bad_request(f"Unknown sample document: {document_id}", "unknown_document")
        selected_documents.append(document)

    for document in request.custom_documents:
        if len(document.text) > settings.max_upload_chars:
            raise bad_request("Document is too large for this demo index.", "document_too_large")
        if not document.text.strip():
            raise bad_request("Document text is empty.", "empty_document")
        selected_documents.append(document)

    if not selected_documents:
        selected_documents = load_sample_documents()

    chunk_size = request.chunk_size or settings.default_chunk_size
    chunk_overlap = request.chunk_overlap or settings.default_chunk_overlap
    chunks = chunk_documents(selected_documents, chunk_size, chunk_overlap)
    VECTOR_STORE.index(chunks)
    INDEXED_DOCUMENTS.clear()
    INDEXED_DOCUMENTS.update({document.id: document for document in selected_documents})
    return IndexResponse(
        document_count=len(selected_documents),
        chunk_count=len(chunks),
        chunks=chunks,
    )


@router.post("/query", response_model=QueryResponse)
def query(request: QueryRequest) -> QueryResponse:
    if not VECTOR_STORE.chunks:
        index_documents(IndexRequest())

    settings = get_settings()
    top_k = request.top_k or settings.retrieval_top_k
    started_at = perf_counter()
    retrieved = VECTOR_STORE.search(request.question, top_k=top_k)
    latency_ms = max(1, round((perf_counter() - started_at) * 1000))
    return build_grounded_answer(
        question=request.question,
        retrieved_chunks=retrieved,
        latency_ms=latency_ms,
        top_k=top_k,
    )


@router.post("/evaluation/run", response_model=EvaluationSummary)
def run_evaluation(request: EvaluationRequest) -> EvaluationSummary:
    examples = request.examples or DEFAULT_EVAL_EXAMPLES
    responses = [query(QueryRequest(question=example.question)) for example in examples]
    return summarize_evaluation(examples, responses)

