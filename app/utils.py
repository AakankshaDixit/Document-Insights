import hashlib
import structlog
import logging

def compute_content_hash(content: str) -> str:
    return hashlib.sha256(content.strip().encode()).hexdigest()

def configure_logging(level="INFO"):
    logging.basicConfig(level=level)
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(level=logging.getLevelName(level))
    )

def get_logger(name):
    return structlog.get_logger(name)