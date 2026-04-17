# Dependency Notes

## Contrato global de dependencias

La fuente de verdad para dependencias Python está en la raíz del repositorio:

- `requirements.txt`: dependencias de runtime pinneadas.
- `requirements-dev.txt`: contrato para desarrollo/tests (incluye runtime + tooling de test).

## Instalación única (todos los componentes Python)

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
```

## Alineación de subcomponentes

`subcase_1b/training_platform/requirements.txt` no declara versiones propias: reexporta `../../requirements.txt` para evitar drift y mantener una sola versión efectiva por paquete.
