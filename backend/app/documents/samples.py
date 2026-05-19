from pathlib import Path

from app.models.schemas import SourceDocument

ROOT = Path(__file__).resolve().parents[3]
SAMPLE_DATA_DIR = ROOT / "sample-data"


def load_sample_documents() -> list[SourceDocument]:
    policy_path = SAMPLE_DATA_DIR / "enterprise_policy.txt"
    return [
        SourceDocument(
            id="acme-ai-governance-policy",
            title="Acme Analytics AI Governance Policy",
            kind="sample",
            text=policy_path.read_text(encoding="utf-8"),
            metadata={
                "domain": "enterprise-ai-governance",
                "source": "synthetic-sample",
            },
        )
    ]
