"""Run the complete backend integration test suite."""

import os
import subprocess
import sys

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    integration_script = os.path.join(script_dir, "run_integration_tests.py")
    ret = subprocess.call([sys.executable, integration_script])
    sys.exit(ret)
