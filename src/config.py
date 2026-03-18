import os

# ---------------------------------------------------------------------------
# Credentials / Configuration
# ---------------------------------------------------------------------------
# We load the API key from environment variables so it doesn't live in source.
# Place your Tripo API key in a .env file at the project root:
#
#   TRIPO_API_KEY=tsk_YOUR_REAL_KEY
#
# The library python-dotenv is supported if installed, otherwise we fall back
# to a simple .env parser.

ENV_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')

# Load environment variables from .env if available.
# We avoid a hard dependency on python-dotenv, but will use it if installed.
try:
    import importlib

    dotenv = importlib.import_module("dotenv")
    dotenv.load_dotenv(ENV_FILE)
except (ImportError, ModuleNotFoundError):
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())


API_KEY: str = os.getenv('TRIPO_API_KEY') or ""
if not API_KEY:
    raise RuntimeError(
        'Missing Tripo API key. Set TRIPO_API_KEY in your environment or in .env.'
    )


# Tripo API base URL (used for task and upload endpoints)
BASE_URL = os.getenv('TRIPO_API_BASE_URL', 'https://api.tripo3d.ai/v2/openapi')

# Root directory of the project (repo root)
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))

# Output directory (defaults to <repo>/output)
OUTPUT_DIR = os.path.abspath(os.getenv('OUTPUT_DIR', os.path.join(ROOT_DIR, 'output')))

# Input image path (can be overridden via .env or environment variable)
# Example in .env:
#   INPUT_IMAGE_PATH=input_images/photo.jpg
INPUT_IMAGE_PATH = os.path.abspath(
    os.getenv(
        'INPUT_IMAGE_PATH',
        os.path.join(ROOT_DIR, 'input_images', 'images.jpg'),
    )
)
