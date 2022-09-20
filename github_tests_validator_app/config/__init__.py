import logging
import os

import google.cloud.logging

if os.getenv("ENV", "") == "PROD":
    logging_client = google.cloud.logging.Client()
    logging_client.get_default_handler()
    logging_client.setup_logging()
else:
    FORMAT = "%(asctime)s - %(levelname)s: %(message)s"
    DATEFMT = "%H:%M:%S"
    logging.basicConfig(
        format=FORMAT,
        level=logging.INFO,
        datefmt=DATEFMT,
    )

    if logging.getLogger("uvicorn") and logging.getLogger("uvicorn").handlers:
        logging.getLogger("uvicorn").removeHandler(logging.getLogger("uvicorn").handlers[0])
