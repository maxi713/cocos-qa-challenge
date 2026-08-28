import requests
from config.settings import BASE_URL, CANDIDATE_ID, BUGS_TIER
from utils.logger import get_logger

logger = get_logger(__name__)


class ApiClient:
    """Wraps a requests.Session with X-Enable-Bugs/X-Candidate-Id as session-level
    defaults. Pass headers={"X-Candidate-Id": None} on a call to drop a default
    header for that single request (used by negative header tests)."""

    def __init__(self, base_url=None, candidate_id=None, bugs_tier=None):
        self.base_url = base_url or BASE_URL
        self.session = requests.Session()
        self.session.headers.update(
            {
                "X-Enable-Bugs": bugs_tier or BUGS_TIER,
                "X-Candidate-Id": candidate_id or CANDIDATE_ID,
            }
        )

    def get(self, endpoint, params=None, headers=None):
        logger.info(f"GET {endpoint} params={params}")
        response = self.session.get(
            self.base_url + endpoint, params=params, headers=headers
        )
        logger.info(f"Response status: {response.status_code}")
        return response

    def post(self, endpoint, payload=None, headers=None):
        logger.info(f"POST {endpoint}")
        logger.info(f"Payload: {payload}")
        response = self.session.post(
            self.base_url + endpoint, json=payload, headers=headers
        )
        logger.info(f"Response status: {response.status_code}")
        return response
