import logging

FORMAT = "%(asctime)s - %(levelname)s: %(message)s"
DATEFMT = "%H:%M:%S"
logging.basicConfig(
    format=FORMAT,
    level=logging.INFO,
    datefmt=DATEFMT,
)

logging.getLogger("uvicorn").removeHandler(logging.getLogger("uvicorn").handlers[0])
