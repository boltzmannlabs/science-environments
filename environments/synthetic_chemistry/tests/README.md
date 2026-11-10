# Testing

From the repository root:

```sh
python -m unittest discover -s environments/synthetic_chemistry/tests -v
```

The tests check the sanitized 16-route dataset, reconstructed step counts, numeric model percentage bounds, actual target consistency, the derived illustrative arithmetic, and top0's flagged condition failures. They do not rerun the external service or prove chemical feasibility. Regeneration of the DOCX is a separate optional dependency check.
