import argparse
import os
from pathlib import Path
import logging
import shutil
import time

def _needs_copy(src: Path, rep: Path) -> bool:
    if not rep.exists():
        return True
    try:
        src_stat = src.stat()
        rep_stat = rep.stat()
        if src_stat.st_size != rep_stat.st_size:
            return True
        if int(src_stat.st_mtime) != int(rep_stat.st_mtime):
            return True
        return False
    except Exception:
        return True

def _sync_folders(source: Path, replica: Path, logger: logging.Logger):
    logger.info(f"Syncing from {source} to {replica}")

    #adding and updating files from source to replica
    for root, dirs, files in os.walk(source):
        src_root = Path(root)
        rel = src_root.relative_to(source)
        rep_root = replica.joinpath(rel)

        # checking if replica directory exists
        if not rep_root.exists():
            rep_root.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {rep_root}")

        # coping or updating files from source to replica
        for name in files:
            src_file = src_root / name
            rep_file = rep_root / name
            try:
                if _needs_copy(src_file, rep_file):
                    shutil.copy2(src_file, rep_file)
                    logger.info(f"Copied/Updated file: {rep_file}")
            except Exception as e:
                logger.exception(f"Failed to copy {src_file} -> {rep_file}: {e}")
    
    # removing files and directories from replica that are not in source
    for root, dirs, files in os.walk(replica, topdown=False):
        rep_root = Path(root)
        rel = rep_root.relative_to(replica)
        src_root = source.joinpath(rel)

        # removing files not in source
        for name in files:
            rep_file = rep_root / name
            src_file = src_root / name
            if not src_file.exists():
                try:
                    rep_file.unlink()
                    logger.info(f"Removed file: {rep_file}")
                except Exception as e:
                    logger.exception(f"Failed to remove file {rep_file}: {e}")

        # removing directories not in source
        for name in dirs:
            rep_dir = rep_root / name
            src_dir = src_root / name
            if not src_dir.exists():
                try:
                    shutil.rmtree(rep_dir)
                    logger.info(f"Removed directory: {rep_dir}")
                except Exception as e:
                    logger.exception(f"Failed to remove directory {rep_dir}: {e}")

def run_periodic_sync(source: Path, replica: Path, interval: float, amount: int, log_path: Path, logger: logging.Logger):
    logger.info(f"Starting periodic sync from {source} to {replica} every {interval} seconds, {amount} times. Logs at {log_path}")

    for i in range(amount):
        logger.info(f"Sync iteration {i+1}/{amount} started.")
        _sync_folders(source, replica, logger)
        logger.info(f"Sync iteration {i+1}/{amount} completed.")
        if i < amount - 1:
            time.sleep(interval)
    logger.info("Periodic sync completed.")

def _setup_logger(log_path: Path) -> logging.Logger:
    # create logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO) # Set to INFO or DEBUG as needed

    # set formatting
    formatter = logging.Formatter('%(asctime)s %(name)s [%(levelname)s]: %(message)s')

    # create file handler
    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

def main():
    # arguments I am suposed to get 
    # - path to source folder
    # - path to replica folder
    # - interval between synchronizations
    # - amount of synchronizations
    # - path to log file


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

    # logger directory validation
    if not args.log.parent.exists():
        parser.error(f"log file directory does not exist: {args.log.parent}")
    
    # logger setup
    logger = _setup_logger(args.log)

    # basic validation
    if not args.source.exists() or not args.source.is_dir():
        parser.error(f"source folder does not exist or is not a directory: {args.source}")
    if not args.replica.exists() or not args.replica.is_dir():
        parser.error(f"replica folder does not exist or is not a directory: {args.replica}")
    if args.interval <= 0:
        parser.error("interval must be a positive number")
    if args.amount <= 0:
        parser.error("amount must be a positive integer")

    logger.debug("Arguments parsed successfully:")
    logger.debug(f"Source folder: {args.source}")
    logger.debug(f"Replica folder: {args.replica}")
    logger.debug(f"Interval: {args.interval} seconds")
    logger.debug(f"Amount: {args.amount}")
    logger.debug(f"Log file: {args.log}")

    run_periodic_sync(
        source=args.source,
        replica=args.replica,
        interval=args.interval,
        amount=args.amount,
        log_path=args.log,
        logger=logger
    )


if __name__ == "__main__":
    main()