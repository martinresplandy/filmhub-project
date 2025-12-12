.PHONY: all install startDB migrate super_migrate run test clear wait_for_db

# **** BACKEND TARGETS **** #

backend_local : clear install startDB migrate_local test_local run clear

backend_ci : clear install migrate_ci run clear

install:
	@echo "NOTE : You first need to set up a virtual environment."
	@echo "Building the project..."
	pip install -r ./api/requirements.txt
	@echo "Build completed."

wait_for_db: install
	@echo "Waiting for PostgreSQL to be ready..."
	SUCCESS_FLAG=1; \
	for i in $$(seq 1 15); do \
		if docker compose exec -T postgres pg_isready -h localhost -U myuser -d mydb > /dev/null 2>&1; then \
			echo "PostgreSQL is fully available after $$i attempts."; \
			SUCCESS_FLAG=0; \
			break; \
		fi; \
		echo "Waiting for PostgreSQL ($$i/15)..."; \
		sleep 2; \
	done; \
	if [ "$$SUCCESS_FLAG" -ne 0 ]; then \
		echo "PostgreSQL failed to start/initialize. Exiting."; \
		docker compose logs postgres; \
		exit 1; \
	fi

wait_for_ci_db: install
	@echo "Waiting for PostgreSQL in CI to be ready..."
	SUCCESS_FLAG=1; \
	for i in $$(seq 1 20); do \
		if PGPASSWORD=$$DB_PASSWORD pg_isready -h $$DB_HOST -U $$DB_USER -d $$DB_NAME > /dev/null 2>&1; then \
			echo "PostgreSQL is fully available after $$i attempts."; \
			SUCCESS_FLAG=0; \
			break; \
		fi; \
		echo "Waiting for PostgreSQL ($$i/20)..."; \
		sleep 3; \
	done; \
	if [ "$$SUCCESS_FLAG" -ne 0 ]; then \
		echo "PostgreSQL failed to start/initialize. Exiting."; \
		exit 1; \
	fi

startDB: install
	@echo "Starting the PostgreSQL database via Docker Compose..."
	docker compose up -d postgres
	@echo "PostgreSQL database started."

migrate_local: install wait_for_db
	@echo "Running database migrations for local setup..."
	python manage.py makemigrations
	python manage.py migrate
	@echo "Database migrations completed."

migrate_ci : install wait_for_ci_db
	@echo "Running database migrations for CI..."
	python manage.py makemigrations
	python manage.py migrate
	@echo "Database migrations for CI completed."

run: install startDB wait_for_db
	@echo "Starting the development server..."
	python manage.py runserver

test_local: install migrate_local
	@echo "Running tests for local setup..."
	python manage.py test api.tests
	@echo "Tests completed."

test_ci: install migrate_ci
	@echo "Running tests for CI..."
	python manage.py test
	@echo "Tests completed."

clear:
	@echo "Cleaning up DB files and Docker container..."
	rm -f *.sqlite3
	rm -rf api/__pycache__
	find ./api/migrations ! -name '__init__.py' -type f -exec rm -f {} +
	docker compose down -v
	@echo "Cleanup completed."