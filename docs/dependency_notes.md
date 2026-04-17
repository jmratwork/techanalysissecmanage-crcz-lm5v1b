# Dependency Notes

## Contrato global de dependencias

The source of truth for Python dependencies is in the root of the repository:

- `requirements.txt`: dependencias de runtime pinneadas.
- `requirements-dev.txt`: contrato para desarrollo/tests (incluye runtime + tooling de test).

## Single installation (all Python components)

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
```

## Subcomponent alignment

`subcase_1b/training_platform/requirements.txt` does not declare its own versions: it re-exports `../../requirements.txt` to avoid drift and maintain a single effective version per package.
