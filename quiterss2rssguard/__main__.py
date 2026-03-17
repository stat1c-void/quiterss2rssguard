import argparse
import logging
import sys
from argparse import Namespace
from pathlib import Path

from .store.quiterss import QuiteRssStore

# TODO: use argparse to get two arguments: source db path and target db path
#   - check existance of both files
#   - make a backup of target (use date-time as part of backup name)
#   - call data migration


def main() -> None:
    """
    Main entry point for the database migration script.

    Parses command-line arguments, initializes logging, reads feeds from the
    source QuiteRSS database, and logs them.
    """
    args = init_app()
    logger = logging.getLogger("quiterss2rssguard")

    # Validate source path
    if not args.source.exists():
        logger.error("source database file not found: %s", args.source)
        sys.exit(1)

    # Stub logic: Read feeds from source and log them
    try:
        with QuiteRssStore(args.source) as store:
            feeds = store.read_feeds()
            logger.info("found %d feeds in source database", len(feeds))
            for feed in feeds:
                logger.info("feed: %s", feed)
    except Exception as e:
        logger.error("error reading source database: %s", e)
        sys.exit(1)


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
        help="Path to the RSS Guard target database file (currently ignored).",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
