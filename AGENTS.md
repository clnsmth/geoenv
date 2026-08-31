# Agent Guidelines for geoenv

## Overview & Architecture
`geoenv` resolves geographic geometries (GeoJSON Points and Polygons) into environmental semantics using spatial datasets and SSSOM vocabulary mappings (defaulting to ENVO).
- **Resolver**: Main coordinator querying data sources concurrently using asynchronous I/O (`aiohttp`).
- **DataSource (ABC)**: Strategy base class located in `src/geoenv/data_sources/` defining data source behavior.
- **Environment**: Encapsulates results and raw terms returned by a data source.
- **Geometry**: Validates and transforms GeoJSON inputs.
- **Response**: GeoJSON Feature wrapper managing semantic mappings and export formats.

## Environment & Dependency Management
- **Tooling**: Use `uv` exclusively.
- **Installation**: `uv sync --extra dev`
- **Dependencies**: Abstract version ranges in `pyproject.toml` (do not commit `uv.lock`).

## Quality & Verification Commands
- **Run Tests**: `uv run pytest`
- **Run Tests with Coverage**: `uv run pytest tests/ --cov=geoenv --cov-report=xml`
- **Format Code**: `uv run ruff format src/ tests/`
- **Lint Code**: `uv run ruff check src/ tests/`
- **Build Docs**: `uv run make html --directory docs/`

## Code & Design Standards
- **Style & Linting**: Formatted and linted with `ruff`.
- **Docstrings**: PEP 287 reStructuredText docstrings for all public modules, classes, and methods.
- **Logging**: Use `daiquiri` with structured metadata.
- **Error Handling**: Raise informative, actionable exceptions at the relevant layer.
- **Adding Data Sources**: Subclass `DataSource`, register in `src/geoenv/data_sources/__init__.py`, provide SSSOM mapping files, and add mock tests under `tests/data_sources/`.

## Commits & Branching
- **Branch Strategy**: Branch from `main` using feature branches (e.g. `123-feature-name`). Target PRs to `main`.
- **Commit Format**: Angular convention (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`).
- **Header Limit**: ≤ 52 characters.
- **Body Limit**: Wrapped at 72 characters explaining *what* and *why*. Reference issues (e.g., `Closes #123`).
