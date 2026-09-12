"""Entry point: `python3 -m gcs` launches the telemetry server + dashboard."""
import sys

from .server import main

if __name__ == "__main__":
    sys.exit(main())
