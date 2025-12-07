.PHONY: all install startDB migrate super_migrate run test clear wait_for_db

# **** BACKEND TARGETS **** #

backend : install startDB migrate run clear

super_backend : install startDB super_migrate run clear

install:
	@echo "NOTE : You first need to set up a virtual environment."
	@echo "Building the project..."
	pip install -r ./api/requirements.txt
	@echo "Build completed."

wait_for_db: startDB
	@echo "Waiting for PostgreSQL service to be HEALTHY..."
	SUCCESS_FLAG=1; \
	for i in $$(seq 1 10); do \
		STATUS=$$(docker compose ps -q postgres | xargs docker inspect --format '{{.State.Health.Status}}'); \
		if [ "$$STATUS" = "healthy" ]; then \
			echo "PostgreSQL is ready and healthy after $$i checks."; \
			SUCCESS_FLAG=0; \
			break; \
		fi; \
		if [ "$$STATUS" = "starting" ] || [ "$$STATUS" = "unhealthy" ]; then \
			echo "PostgreSQL status: $$STATUS ($$i/10)..."; \
		else \
			echo "PostgreSQL container status: $$STATUS. Aborting."; \
			exit 1; \
		fi; \
		sleep 5; \
	done; \
	if [ "$$SUCCESS_FLAG" -ne 0 ]; then \
		echo "PostgreSQL failed to become healthy after 50 seconds. Exiting."; \
		exit 1; \
	fi

startDB: install
	@echo "Starting the PostgreSQL database via Docker Compose..."
	docker compose up -d postgres
	@echo "PostgreSQL database started."

migrate: install wait_for_db
	@echo "Running database migrations..."
	python manage.py makemigrations
	python manage.py migrate
	@echo "Database migrations completed."

super_migrate: install wait_for_db
	@echo "Running database migrations..."
	python manage.py makemigrations
	python manage.py migrate
	@echo "Initializing database with super user..."
	python manage.py createsuperuser
	@echo "Database migrations completed."

run: install startDB wait_for_db
	@echo "Starting the development server..."
	python manage.py runserver

test: install startDB wait_for_db
	@echo "Running tests..."
	python manage.py test api.tests
	@echo "Tests completed."

clear:
	@echo "Cleaning up DB files and Docker container..."
	rm -f *.sqlite3
	rm -rf api/__pycache__
	find ./api/migrations ! -name '__init__.py' -type f -exec rm -f {} +
	docker compose down -v
	@echo "Cleanup completed."