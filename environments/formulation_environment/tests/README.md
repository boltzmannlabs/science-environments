# Validation tests

Run `python -m unittest discover -s tests -v` from this environment. The tests independently check composition gates, expected numeric exports, source integrity, held-out splits, bounded fits, empty planned observations and exact task-folder links. `scripts/validate_environment.py` adds a publication/privacy scan and writes a receipt. Full offline replay is a separate real execution and is compared against curated values; no lab results are invented.
