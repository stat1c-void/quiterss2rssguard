import argparse
import contextlib
import logging
import shutil
import sys
from argparse import Namespace
from datetime import datetime, timedelta
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
        # Load all feeds from source and store them in target
        with contextlib.ExitStack() as stack:
            source_store = stack.enter_context(QuiteRssStore(args.source))
            target_store = stack.enter_context(RssGuardStore(args.target))

            feeds = source_store.read_feeds()
            logger.info("found %d feeds in source database", len(feeds))

            if not feeds:
                logger.info("no feeds found to migrate")
                return

            for feed in feeds:
                # Store feed in target
                target_store.store_feed(feed)

                # Load news items for this feed and save them to target
                news_items = source_store.read_news_items(feed, args.skip_older_than)
                for item in news_items:
                    target_store.store_news_item(item)

                logger.info("processed feed '%s' with %d news items", feed.name, len(news_items))

        logger.info("migration completed successfully")
    except Exception:
        logger.exception("migration failed")
        sys.exit(1)


def backup_database(path: Path) -> Path:
    """
    Creates a timestamped backup of the database file.

    :param path: Path to the database file to backup
    :type path: Path
    :return: Path to the created backup file
    :rtype: Path
    """
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = path.with_suffix(f".{timestamp}.bak")
    shutil.copy(path, backup_path)
    return backup_path


def init_app() -> Namespace:
    # Initialize logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        prog="quiterss2rssguard", description="Migrate feed data from QuiteRSS to RSS Guard."
    )
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
    parser.add_argument(
        "--skip-older-than",
        type=int,
        default=365,
        help="Skip deleted news items older than N days (default: 365)",
    )
    args = parser.parse_args()
    args.skip_older_than = timedelta(days=args.skip_older_than)
    return args


if __name__ == "__main__":
    main()
