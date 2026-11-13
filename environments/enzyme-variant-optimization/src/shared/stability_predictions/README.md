# Shared stability-prediction submission code

`submit_ddgun_once.py` is the exact script used by the native scientist for the additional RML/LEH DDGun predictions. It checks parent/candidate hashes and full combined mutations, reserves an attempt before submission, and does not automatically repeat an uncertain POST.
It expects `inputs/ddgun_RML_WT.json` or `inputs/ddgun_LEH_WT.json` and `jobs/` in the parent workspace. This is archived execution code, not an instruction to resubmit completed jobs 99400/99401. Their inputs and results are stored with the corresponding tasks.
The dated extraction/verification scripts and procedural-skill snapshot remain in the local execution archive. The maintained report builder is `src/benchmark_reports.py`.

[Executed EvoEF1 paired-WT comparison](evoef/README.md) contains the actual whole-variant driver and strict sequence/energy parser used for the open-source alternative assessment.
