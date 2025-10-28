import argparse
from pathlib import Path
import logging
from venv import logger






def main():
    # arguments I am suposed to get 
    # - path to source folder
    # - path to replica folder
    # - interval between synchronizations
    # - amount of synchronizations
    # - path to log file

    # logger setup
    logging.basicConfig( encoding='utf-8', level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    # parsing command line arguments
    parser = argparse.ArgumentParser(
        description="Read synchronization parameters: source, replica, interval, amount, log path"
    )
    parser.add_argument("source", type=Path, help="path to source folder")
    parser.add_argument("replica", type=Path, help="path to replica folder")
    parser.add_argument("interval", type=float, help="interval between synchronizations (seconds)")
    parser.add_argument("amount", type=int, help="amount of synchronizations")
    parser.add_argument("log", type=Path, help="path to log file")

    args = parser.parse_args()

    # basic validation
    if not args.source.exists() or not args.source.is_dir():
        parser.error(f"source folder does not exist or is not a directory: {args.source}")
    if not args.replica.exists() or not args.replica.is_dir():
        parser.error(f"replica folder does not exist or is not a directory: {args.replica}")
    if args.interval <= 0:
        parser.error("interval must be a positive number")
    if args.amount <= 0:
        parser.error("amount must be a positive integer")
    if not args.log.parent.exists():
        parser.error(f"log file directory does not exist: {args.log.parent}")

    logger.debug("Arguments parsed successfully:")
    logger.debug(f"Source folder: {args.source}")
    logger.debug(f"Replica folder: {args.replica}")
    logger.debug(f"Interval: {args.interval} seconds")
    logger.debug(f"Amount: {args.amount}")
    logger.debug(f"Log file: {args.log}")


    return args

if __name__ == "__main__":
    main()