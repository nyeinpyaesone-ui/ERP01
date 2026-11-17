.PHONY: help build up down logs shell test check migrate createsuperuser platform-up platform-down backup

help:
	@echo "ERP01 development and operations"
	@echo "  make build            Build core web and frontend images"
	@echo "  make up               Start core ERP01 stack"
	@echo "  make platform-up      Start ERP01 plus gateway, finance and monitoring"
	@echo "  make down             Stop services; keep persistent volumes"
	@echo "  make platform-down    Stop optional platform stack; keep volumes"
	@echo "  make logs             Follow core service logs"
	@echo "  make test             Run Django tests"
	@echo "  make check            Run Django checks and migration drift check"
	@echo "  make migrate          Apply Django migrations"
	@echo "  make createsuperuser  Create the first staff account"
	@echo "  make backup           Write a database backup to ./backups/"

build:
	docker compose build

up:
	docker compose up -d

platform-up:
	docker compose -f docker-compose.yml -f docker-compose.platform.yml up -d --build

down:
	docker compose down

platform-down:
	docker compose -f docker-compose.yml -f docker-compose.platform.yml down

logs:
	docker compose logs -f

shell:
	docker compose exec web sh

test:
	DJANGO_SETTINGS_MODULE=config.settings.test pytest -o addopts=""

check:
	DJANGO_SETTINGS_MODULE=config.settings.test python src/manage.py check
	DJANGO_SETTINGS_MODULE=config.settings.test python src/manage.py makemigrations --check --dry-run

migrate:
	docker compose exec web python src/manage.py migrate --noinput

createsuperuser:
	docker compose exec web python src/manage.py createsuperuser

backup:
	mkdir -p backups
	docker compose exec -T postgres sh -c 'pg_dump -U "$$POSTGRES_USER" "$$POSTGRES_DB"' > "backups/erp01-$$(date +%Y%m%d-%H%M%S).sql"

clean-build:
	docker compose down
	docker builder prune -f
