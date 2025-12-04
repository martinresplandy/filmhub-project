.PHONY: all install startDB migrate super_migrate run test clear wait_for_db

# **** BACKEND TARGETS **** #

backend : install startDB migrate test run clear

super_backend : install startDB super_migrate test run clear

install:
	@echo "NOTE : You first need to set up a virtual environment."
	@echo "Building the project..."
	pip install -r ./api/requirements.txt
	@echo "Build completed."

wait_for_db: install
	@echo "Waiting for PostgreSQL to be ready..."
    # Netcat (nc) checks if the host (localhost) and port (5432) are open.
	SUCCESS_FLAG=1; \
	for i in $$(seq 1 10); do \
		nc -z -w1 localhost 5432; \
		if [ $$? -eq 0 ]; then \
			echo "PostgreSQL est disponible après $$i tentatives."; \
			SUCCESS_FLAG=0; \
			break; \
		fi; \
		echo "Waiting for PostgreSQL ($$i/10)..."; \
		sleep 5; \
	done
	if [ $$SUCCESS_FLAG -ne 0 ]; then \
		echo "PostgreSQL failed to start after 50 seconds. Exiting."; \
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
	python manage.py test api
	@echo "Tests completed."

clear:
	@echo "Cleaning up DB files and Docker container..."
	rm -f *.sqlite3
	find ./api/migrations ! -name '__init__.py' -type f -exec rm -f {} +
	docker compose down -v
	@echo "Cleanup completed."