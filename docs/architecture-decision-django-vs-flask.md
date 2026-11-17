# Architecture Decision: Keep Django/DRF

## Decision

ERP01 should remain a Django and Django REST Framework application rather than migrate to Flask.

## Context

The repository already contains a Django project layout with `config/` settings and URL routing, a `src/manage.py` entrypoint, pytest-django configuration, DRF settings, and an implemented inventory module under `src/modules/`. Replacing this foundation with Flask would require reworking settings, migrations, URL routing, tests, CI commands, and documentation before adding equivalent ERP features.

## Rationale

- Django already provides the ERP primitives this project needs: ORM models, migrations, authentication, admin, permissions, and structured app boundaries.
- DRF is already configured globally and the existing inventory module exposes REST viewsets through `config/urls.py` and `src/api/urls.py`.
- Missing concepts from the Flask tree can be ported incrementally as Django apps under `src/modules/`, preserving the current architecture and test setup.
- Keeping one framework avoids maintaining duplicate backend trees and reduces migration risk.

## Implementation Notes

- Do not add a separate Flask `backend/` tree.
- Add missing ERP capabilities as Django modules under `src/modules/`.
- Keep top-level API routing in `config/urls.py` and module API registration in `src/api/urls.py`.
- Use Django auth and DRF/SimpleJWT endpoints for API authentication.
