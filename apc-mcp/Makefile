SHELL := /usr/bin/env bash

.PHONY: up down logs db psetup nsetup py-dev node-dev lint fmt

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

db: up
	@echo "Open Adminer: http://localhost:8080 (System: PostgreSQL, Server: db, User: apc_user)"

psetup:
	./scripts/dev/setup_python.sh

nsetup:
	./scripts/dev/setup_node.sh

py-dev:
	./scripts/dev/run_mcp_stub.sh

node-dev:
	./scripts/dev/run_launcher.sh

lint:
	./scripts/dev/lint.sh

fmt:
	./scripts/dev/format.sh
