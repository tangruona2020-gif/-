import json
import logging

from app.config import ROOT, get_settings


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        fields: dict[str, object] = {
            "level": record.levelname,
            "message": record.getMessage(),
        }
        for key in (
            "source",
            "scan_run_id",
            "url",
            "adapter",
            "step",
            "status",
            "error_type",
            "error_message",
            "duration_ms",
        ):
            fields[key] = getattr(record, key, None)
        return json.dumps(fields, ensure_ascii=False)


def configure_logging() -> None:
    log_dir = ROOT / "data" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(log_dir / "app.jsonl", encoding="utf-8")
    handler.setFormatter(JsonFormatter())
    logging.basicConfig(level=get_settings().log_level, handlers=[handler, logging.StreamHandler()])
