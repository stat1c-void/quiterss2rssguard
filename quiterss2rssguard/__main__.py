import argparse
import logging
import shutil
import sys
from argparse import Namespace
from datetime import datetime
from pathlib import Path

from .store.quiterss import QuiteRssStore
from .store.rssguard import RssGuardStore


def main() -> None:
    """
    Main entry point for the database migration script.

    Parses command-line arguments, initializes logging, reads feeds from the
    source QuiteRSS database, and stores them in the target RSS Guard database.
    """
    args = init_app()
    logger = logging.getLogger("quiterss2rssguard")

    # 1. Backup target database if it exists
    if args.target.exists():
        backup_path = backup_database(args.target)
        logger.info("backed up target database to %s", backup_path)

    # 2. Migration logic
    try:
        # Load all feeds from source
        with QuiteRssStore(args.source) as source_store:
            feeds = source_store.read_feeds()
            logger.info("found %d feeds in source database", len(feeds))

        if not feeds:
            logger.info("no feeds found to migrate")
            return

        # Store all feeds in target
        with RssGuardStore(args.target) as target_store:
            for feed in feeds:
                target_store.store_feed(feed)
                logger.info("migrated feed: %s", feed)

        logger.info("migration completed successfully")
    except Exception:
        logger.exception("migration failed")
        sys.exit(1)


def backup_database(path: Path) -> Path:
    """
    Creates a timestamped backup of the database file.

    Args:
        path: Path to the database file to backup

    Returns:
        Path to the created backup file
    """
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = path.with_suffix(f".{timestamp}.bak")
    shutil.copy2(path, backup_path)
    return backup_path


def init_app() -> Namespace:
    # Initialize logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Migrate feed data from QuiteRSS to RSS Guard.")
    parser.add_argument(
        "source",
        type=Path,
        help="Path to the QuiteRSS source database file.",
    )
    parser.add_argument(
        "target",
        type=Path,
        help="Path to the RSS Guard target database file.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
