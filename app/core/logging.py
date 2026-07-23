# app/core/logging.py
import logging


def setup_logging() -> None:
    """Configures the application's logging system. Call once, at startup."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s [%(name)s] %(message)s',
    )


# Módulo-level logger, pronto pra ser importado em qualquer arquivo da app
logger = logging.getLogger()
