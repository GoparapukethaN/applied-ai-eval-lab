import {
  demoEvaluation,
  demoIndex,
  demoQuery,
  demoUpload
} from "../lib/demo.ts";

const starterQuestions = [
  "What should the team do with secrets?",
  "How quickly should severity one incidents notify the security lead?",
  "What must be documented during AI vendor review?",
  "What should AI evaluation reports include?"
];

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

function assertUniqueChunkIds(chunks, label) {
  const ids = chunks.map((chunk) => chunk.id);
  const uniqueIds = new Set(ids);
  assert(uniqueIds.size === ids.length, `${label} has duplicate chunk ids: ${ids.join(", ")}`);
}

function assertChunkCount(response, label) {
  assert(
    response.chunk_count === response.chunks.length,
    `${label} chunk_count=${response.chunk_count} but returned ${response.chunks.length} chunks`
  );
}

function assertCitationsPointToRetrievedEvidence(question) {
  const response = demoQuery(question);
  const retrievedIds = new Set(response.retrieved_chunks.map((item) => item.chunk.id));
  for (const citation of response.citations) {
    assert(
      retrievedIds.has(citation.chunk_id),
      `citation ${citation.id} for "${question}" points to ${citation.chunk_id}, which was not retrieved`
    );
  }
}

const indexResponse = demoIndex();
const uploadResponse = demoUpload();
const evaluation = demoEvaluation();

assertChunkCount(indexResponse, "demoIndex");
assertChunkCount(uploadResponse, "demoUpload");
assertUniqueChunkIds(indexResponse.chunks, "demoIndex");
assert(evaluation.example_count === evaluation.items.length, "evaluation example_count must match items length");

for (const question of starterQuestions) {
  assertCitationsPointToRetrievedEvidence(question);
}

console.log("static demo data verification passed");
