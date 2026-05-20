PYTHON ?= python3
NPM ?= npm

.PHONY: install-backend install-frontend test-backend audit typecheck build build-pages compose-check docker-check verify

install-backend:
	$(PYTHON) -m pip install -e "backend[dev]"

install-frontend:
	cd frontend && $(NPM) ci

test-backend:
	$(PYTHON) -m pytest backend/tests

audit:
	cd frontend && $(NPM) audit --audit-level=moderate

typecheck:
	cd frontend && $(NPM) run typecheck

build:
	cd frontend && $(NPM) run build

build-pages:
	cd frontend && $(NPM) run build:pages

compose-check:
	docker compose config --quiet

docker-check:
	./scripts/verify-docker.sh

verify:
	./scripts/verify-local.sh
