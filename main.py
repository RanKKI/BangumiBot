import logging

from dotenv import load_dotenv

from bangumi import Bangumi
from bangumi.util import init_folders, setup_logger

logger = logging.getLogger(__name__)


def main():
    load_dotenv(".env")
    setup_logger()
    init_folders()
    try:
        Bangumi().run()
    except KeyboardInterrupt:
        logger.info("Shutting down...")

if __name__ == '__main__':
    main()
