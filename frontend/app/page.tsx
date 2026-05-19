"use client";

import {
  Activity,
  BarChart3,
  CheckCircle2,
  Database,
  FileSearch,
  Play,
  RefreshCw,
  ShieldCheck,
  SlidersHorizontal
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import {
  askQuestion,
  getSampleDocuments,
  indexSampleDocument,
  runEvaluation
} from "@/lib/api";
import type {
  DocumentSummary,
  EvaluationSummary,
  IndexResponse,
  QueryResponse
} from "@/lib/types";

const starterQuestions = [
  "What should evaluation reports include?",
  "How quickly should severity one incidents notify the security lead?",
  "What must be documented during AI vendor review?"
];

export default function Home() {
  const [documents, setDocuments] = useState<DocumentSummary[]>([]);
  const [activeDocumentId, setActiveDocumentId] = useState<string>("");
  const [index, setIndex] = useState<IndexResponse | null>(null);
  const [question, setQuestion] = useState(starterQuestions[0]);
  const [answer, setAnswer] = useState<QueryResponse | null>(null);
  const [evaluation, setEvaluation] = useState<EvaluationSummary | null>(null);
  const [status, setStatus] = useState("Loading workspace");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const selectedDocument = useMemo(
    () => documents.find((document) => document.id === activeDocumentId),
    [documents, activeDocumentId]
  );

  useEffect(() => {
    getSampleDocuments()
      .then((items) => {
        setDocuments(items);
        setActiveDocumentId(items[0]?.id ?? "");
        setStatus("Workspace ready");
      })
      .catch((caught: unknown) => {
        setError(caught instanceof Error ? caught.message : "Unable to load documents");
        setStatus("Backend unavailable");
      });
  }, []);

  async function handleIndex() {
    if (!activeDocumentId) return;
    setBusy(true);
    setError(null);
    setStatus("Indexing document");
    try {
      const result = await indexSampleDocument(activeDocumentId);
      setIndex(result);
      setStatus(`Indexed ${result.chunk_count} chunks`);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Indexing failed");
      setStatus("Indexing failed");
    } finally {
      setBusy(false);
    }
  }

  async function handleAsk() {
    setBusy(true);
    setError(null);
    setStatus("Running grounded query");
    try {
      const result = await askQuestion(question);
      setAnswer(result);
      setStatus("Answer generated with evidence");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Query failed");
      setStatus("Query failed");
    } finally {
      setBusy(false);
    }
  }

  async function handleEvaluate() {
    setBusy(true);
    setError(null);
    setStatus("Running evaluation set");
    try {
      const result = await runEvaluation();
      setEvaluation(result);
      setStatus(`Evaluation ${result.run_id} complete`);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Evaluation failed");
      setStatus("Evaluation failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="workspace">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">
            <FileSearch size={20} />
          </div>
          <div>
            <h1>Applied AI Eval Lab</h1>
            <p>Document intelligence and evaluation workspace</p>
          </div>
        </div>

        <section className="panel">
          <div className="panel-heading">
            <Database size={18} />
            <h2>Documents</h2>
          </div>
          <label className="field-label" htmlFor="document">
            Active collection
          </label>
          <select
            id="document"
            value={activeDocumentId}
            onChange={(event) => setActiveDocumentId(event.target.value)}
          >
            {documents.map((document) => (
              <option key={document.id} value={document.id}>
                {document.title}
              </option>
            ))}
          </select>
          <button type="button" onClick={handleIndex} disabled={busy || !activeDocumentId}>
            {busy ? <RefreshCw className="spin" size={16} /> : <Play size={16} />}
            Index
          </button>
          {selectedDocument ? (
            <dl className="mini-stats">
              <div>
                <dt>Characters</dt>
                <dd>{selectedDocument.char_count.toLocaleString()}</dd>
              </div>
              <div>
                <dt>Domain</dt>
                <dd>{selectedDocument.metadata.domain}</dd>
              </div>
            </dl>
          ) : null}
        </section>

        <section className="panel">
          <div className="panel-heading">
            <ShieldCheck size={18} />
            <h2>Production Notes</h2>
          </div>
          <ul className="check-list">
            <li>Provider-neutral API boundaries</li>
            <li>Local mode requires no API keys</li>
            <li>Evaluation runs expose failures</li>
            <li>Citations trace answers to chunks</li>
          </ul>
        </section>
      </aside>

      <section className="main-panel">
        <header className="topbar">
          <div>
            <p className="eyebrow">Enterprise AI evaluation</p>
            <h2>Ground answers, inspect evidence, measure quality.</h2>
          </div>
          <div className="status-pill">
            <Activity size={16} />
            {status}
          </div>
        </header>

        {error ? <div className="error-banner">{error}</div> : null}

        <section className="grid two">
          <div className="surface query-panel">
            <div className="section-title">
              <FileSearch size={18} />
              <h3>Ask and Cite</h3>
            </div>
            <textarea
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              rows={4}
              aria-label="Question"
            />
            <div className="question-row">
              {starterQuestions.map((item) => (
                <button
                  className="ghost"
                  key={item}
                  type="button"
                  onClick={() => setQuestion(item)}
                >
                  {item}
                </button>
              ))}
            </div>
            <button type="button" onClick={handleAsk} disabled={busy || question.length < 3}>
              {busy ? <RefreshCw className="spin" size={16} /> : <Play size={16} />}
              Run Query
            </button>
          </div>

          <div className="surface metrics-panel">
            <div className="section-title">
              <SlidersHorizontal size={18} />
              <h3>Run Metadata</h3>
            </div>
            <div className="metric-grid">
              <Metric label="Chunks" value={index?.chunk_count ?? 0} />
              <Metric label="Confidence" value={answer ? `${Math.round(answer.confidence * 100)}%` : "0%"} />
              <Metric label="Latency" value={answer ? `${answer.metadata.latency_ms} ms` : "0 ms"} />
              <Metric label="Cost Est." value={answer ? `$${answer.metadata.estimated_cost_usd.toFixed(6)}` : "$0"} />
            </div>
          </div>
        </section>

        <section className="grid two">
          <div className="surface answer-panel">
            <div className="section-title">
              <CheckCircle2 size={18} />
              <h3>Grounded Answer</h3>
            </div>
            {answer ? (
              <>
                <p className="answer">{answer.answer}</p>
                <div className="citation-list">
                  {answer.citations.map((citation) => (
                    <article key={citation.id} className="citation">
                      <strong>{citation.id}</strong>
                      <span>{citation.document_title}</span>
                      <small>{citation.section}</small>
                      <p>{citation.quote}</p>
                    </article>
                  ))}
                </div>
              </>
            ) : (
              <p className="empty-state">Run a query to inspect the grounded answer.</p>
            )}
          </div>

          <div className="surface evidence-panel">
            <div className="section-title">
              <Database size={18} />
              <h3>Retrieved Evidence</h3>
            </div>
            {answer?.retrieved_chunks.length ? (
              <div className="evidence-list">
                {answer.retrieved_chunks.map((item) => (
                  <article key={item.chunk.id} className="evidence">
                    <div>
                      <strong>{item.chunk.section}</strong>
                      <span>{Math.round(item.score * 100)} match</span>
                    </div>
                    <p>{item.chunk.text}</p>
                  </article>
                ))}
              </div>
            ) : (
              <p className="empty-state">Retrieved chunks will appear here.</p>
            )}
          </div>
        </section>

        <section className="surface evaluation-panel">
          <div className="evaluation-heading">
            <div className="section-title">
              <BarChart3 size={18} />
              <h3>Evaluation Dashboard</h3>
            </div>
            <button type="button" onClick={handleEvaluate} disabled={busy}>
              {busy ? <RefreshCw className="spin" size={16} /> : <Play size={16} />}
              Run Eval
            </button>
          </div>

          <div className="metric-grid eval">
            <Metric
              label="Hit Rate"
              value={evaluation ? `${Math.round(evaluation.retrieval_hit_rate * 100)}%` : "0%"}
            />
            <Metric
              label="Citation Coverage"
              value={
                evaluation
                  ? `${Math.round(evaluation.average_citation_coverage * 100)}%`
                  : "0%"
              }
            />
            <Metric
              label="Avg Latency"
              value={evaluation ? `${evaluation.average_latency_ms} ms` : "0 ms"}
            />
            <Metric label="Failures" value={evaluation?.failure_count ?? 0} />
          </div>

          {evaluation ? (
            <div className="eval-table">
              {evaluation.items.map((item) => (
                <article key={item.id} className="eval-row">
                  <div>
                    <strong>{item.question}</strong>
                    <span>{item.retrieval_hit ? "Context hit" : "Needs review"}</span>
                  </div>
                  <p>{item.actual_answer}</p>
                  {item.failure_category ? <small>{item.failure_category}</small> : null}
                </article>
              ))}
            </div>
          ) : (
            <p className="empty-state">Run the curated eval set to see quality signals.</p>
          )}
        </section>
      </section>
    </main>
  );
}

function Metric({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="metric">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

