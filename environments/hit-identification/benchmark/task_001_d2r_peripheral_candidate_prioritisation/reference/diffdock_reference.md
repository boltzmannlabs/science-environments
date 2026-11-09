# DiffDock interpretation reference

Primary sources, accessed2026-11-09: [official README](https://github.com/gcorso/DiffDock/blob/main/README.md) and [inference implementation](https://github.com/gcorso/DiffDock/blob/main/inference.py). Retrieval hashes are retained in `downloads.json`.

The implementation sorts with `np.argsort(confidence)[::-1]`, placing maximum confidence first. The original README describes confidence as pose-prediction quality, not binding affinity, and gives rough confidence bands. The raw run’s Rank0 values independently match the maxima. These sources are used for interpretation; their application code was not executed by this review.
