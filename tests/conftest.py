import sys
from pathlib import Path


def pytest_configure():
    # Ensure the repository root is on sys.path so tests can import local packages
    root = Path(__file__).parent.parent.resolve()
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
