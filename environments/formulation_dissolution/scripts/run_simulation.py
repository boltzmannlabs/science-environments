"""Repository runner; uses the existing simulation wrapper, not a second engine."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from simulation import main

if __name__ == "__main__":
    main()
