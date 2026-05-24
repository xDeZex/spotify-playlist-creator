# dependency-management Specification

## Purpose
TBD - created by archiving change project-scaffolding. Update Purpose after archive.
## Requirements
### Requirement: Dependencies are declared in pyproject.toml
The project SHALL declare its runtime dependencies (`spotipy`, `python-dotenv`) in `pyproject.toml` under `[project].dependencies`.

#### Scenario: Dependencies are installable
- **WHEN** a developer runs `pip install .` or `pip install -e .`
- **THEN** all required packages are installed without manual steps

### Requirement: Requirements file for direct pip install
The project SHALL provide a `requirements.txt` listing pinned or minimum-version runtime dependencies, so the project can also be set up via `pip install -r requirements.txt`.

#### Scenario: Requirements file installs dependencies
- **WHEN** a developer runs `pip install -r requirements.txt`
- **THEN** all runtime dependencies are available in the environment

### Requirement: Project metadata is declared
The `pyproject.toml` SHALL include `[project]` metadata: `name`, `version`, `requires-python` (>= 3.10), and `description`.

#### Scenario: Metadata is present
- **WHEN** a developer inspects `pyproject.toml`
- **THEN** the file contains name, version, requires-python, and description fields

