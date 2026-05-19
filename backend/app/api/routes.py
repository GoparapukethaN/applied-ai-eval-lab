from time import perf_counter
from uuid import uuid4

from fastapi import APIRouter, File, UploadFile

from app.core.config import get_settings
from app.core.errors import bad_request
from app.documents.chunking import chunk_documents
from app.documents.parsing import parse_uploaded_document
from app.documents.samples import load_sample_documents
from app.evaluation.reports import list_reports, save_report
from app.evaluation.scoring import DEFAULT_EVAL_EXAMPLES, summarize_evaluation
from app.generation.grounded import build_grounded_answer
from app.models.schemas import (
    DocumentSummary,
    EvaluationRequest,
    EvaluationSummary,
    ExperimentConfig,
    ExperimentResult,
    ExperimentRunResponse,
    HealthResponse,
    IndexRequest,
    IndexResponse,
    QueryRequest,
    QueryResponse,
    ReportSummary,
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


@router.post("/documents/upload", response_model=IndexResponse)
async def upload_document(file: UploadFile = File(...)) -> IndexResponse:
    settings = get_settings()
    content = await file.read()
    if len(content) > settings.max_upload_chars:
        raise bad_request("Document is too large for this demo index.", "document_too_large")
    document = parse_uploaded_document(
        filename=file.filename or "uploaded-document.txt",
        content_type=file.content_type,
        content=content,
    )
    return index_documents(IndexRequest(custom_documents=[document]))


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
    summary = summarize_evaluation(examples, responses)
    save_report("evaluation", summary.run_id, summary)
    return summary


@router.post("/experiments/run", response_model=ExperimentRunResponse)
def run_experiments(request: EvaluationRequest) -> ExperimentRunResponse:
    examples = request.examples or DEFAULT_EVAL_EXAMPLES
    configs = [
        ExperimentConfig(
            id="focused",
            label="Focused Retrieval",
            top_k=2,
            description="Prioritizes the strongest chunks to reduce noisy citations.",
        ),
        ExperimentConfig(
            id="balanced",
            label="Balanced Retrieval",
            top_k=4,
            description="Default setting for quality, latency, and evidence coverage.",
        ),
        ExperimentConfig(
            id="broad",
            label="Broad Retrieval",
            top_k=6,
            description="Pulls more context for ambiguous questions and review workflows.",
        ),
    ]
    results: list[ExperimentResult] = []
    for config in configs:
        responses = [
            query(QueryRequest(question=example.question, top_k=config.top_k))
            for example in examples
        ]
        results.append(
            ExperimentResult(
                config=config,
                summary=summarize_evaluation(examples, responses),
            )
        )

    winner = min(
        results,
        key=lambda result: (
            result.summary.failure_count,
            -result.summary.retrieval_hit_rate,
            -result.summary.average_citation_coverage,
            result.summary.average_latency_ms,
        ),
    )
    response = ExperimentRunResponse(
        run_id=f"experiment-{uuid4().hex[:8]}",
        winner=winner.config.id,
        results=results,
    )
    save_report("experiment", response.run_id, response)
    return response


@router.get("/reports", response_model=list[ReportSummary])
def reports() -> list[ReportSummary]:
    return list_reports()
