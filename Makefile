PYTHON ?= python3
NPM ?= npm

.PHONY: install-backend install-frontend test-backend audit verify-demo-data typecheck build build-pages verify-static-demo compose-check docker-check verify verify-full

install-backend:
	$(PYTHON) -m pip install -e "backend[dev]"

install-frontend:
	cd frontend && $(NPM) ci

test-backend:
	$(PYTHON) -m pytest backend/tests

audit:
	cd frontend && $(NPM) audit --audit-level=moderate

verify-demo-data:
	cd frontend && $(NPM) run verify:demo-data

typecheck:
	cd frontend && $(NPM) run typecheck

build:
	cd frontend && $(NPM) run build

build-pages:
	cd frontend && $(NPM) run build:pages

verify-static-demo:
	cd frontend && $(NPM) run verify:static-demo

compose-check:
	docker compose config --quiet

docker-check:
	./scripts/verify-docker.sh

verify:
	./scripts/verify-local.sh

verify-full: verify compose-check docker-check
