import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from etl.extract import extract
from etl.load import load
from etl.logger import get_logger
from etl.transform import transform

log = get_logger("pipeline")


def run() -> None:
    start = time.time()
    log.info("== Pipeline start ==")
    raw = extract()
    clean = transform(raw)
    load(clean)
    log.info("== Pipeline finished in %.2fs ==", time.time() - start)


if __name__ == "__main__":
    run()
