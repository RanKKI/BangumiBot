import logging

from dotenv import load_dotenv

from bangumi import Bangumi
from bangumi.api import start_api_server
from bangumi.util import init_folders, setup_logger

logger = logging.getLogger(__name__)


def main():
    load_dotenv(".env")
    setup_logger()
    init_folders()
    Bangumi().run()

if __name__ == '__main__':
    main()
