import pytest
from clients.api_client import ApiClient
from config.settings import BUGS_TIER
from services.instruments_service import InstrumentsService
from utils.logger import get_logger

logger = get_logger(__name__)


def pytest_addoption(parser):
    parser.addoption(
        "--bugs-tier",
        action="store",
        default=None,
        choices=["off", "easy", "medium", "hard"],
        help="Overrides X-Enable-Bugs for the whole run (default: BUGS_TIER from .env, or 'off').",
    )


@pytest.fixture(scope="session")
def bugs_tier(request):
    return request.config.getoption("--bugs-tier") or BUGS_TIER


@pytest.fixture(scope="session")
def api_client(bugs_tier):
    return ApiClient(bugs_tier=bugs_tier)


@pytest.fixture(scope="session")
def instruments_service(api_client):
    return InstrumentsService(api_client)


@pytest.fixture(autouse=True)
def log_test_execution(request):
    logger.info(f"STARTING TEST: {request.node.name}")

    yield

    logger.info(f"FINISHED TEST: {request.node.name}")
