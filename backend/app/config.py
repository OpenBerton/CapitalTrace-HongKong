import os

from dotenv import load_dotenv

load_dotenv()

CCASS_BASE_URL = os.getenv("CCASS_BASE_URL", "https://example-ccass-site.com")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "15"))
