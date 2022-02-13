import json
import subprocess
from pathlib import Path
import os


def test_blender():
    path = Path(os.path.realpath(__file__)).parent / "scripts/blender.py"
    subprocess.run(f"blender --background --python {json.dumps(str(path))}")


if __name__ == "__main__":
    test_blender()
