# enzyme-recovery intermediate receipt

Root cause: guards tested build-time `torch.version.cuda is None` (torch 2.9.1+cu128) although `CUDA_VISIBLE_DEVICES=""` yields cuda.is_available()=False, device_count=0. Correction: `require(not torch.cuda.is_available() and torch.cuda.device_count() == 0, ...)` in both runners; re-freeze runner hashes and keep scientific identity intact. Run ID pythia_cellulase_003 must not be reused.
