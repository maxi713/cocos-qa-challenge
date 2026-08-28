import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "https://dummy-api-topaz.vercel.app")
CANDIDATE_ID = os.getenv("CANDIDATE_ID", "maxi2161")
BUGS_TIER = os.getenv("BUGS_TIER", "off")
