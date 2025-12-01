

.PHONY: all install migrate super_migrate run test clear 

all : clear install migrate test run

super_all : clear install super_migrate test run

install :
	@echo "NOTE : You first need to set up a virtual environment."
	@echo "Building the project..."
	pip install -r ./api/requirements.txt
	@echo "Build completed."

migrate:
	@echo "Running database migrations..."
	python manage.py makemigrations
	python manage.py migrate
	@echo "Database migrations completed."

super_migrate :
	@echo "Running database migrations..."
	python manage.py makemigrations
	python manage.py migrate
	@echo "Initializing database with super user..."
	python manage.py createsuperuser
	@echo "Database migrations completed."

run :
	@echo "Starting the development server..."
	python manage.py runserver

test :
	@echo "Running tests..."
	python manage.py test api
	@echo "Tests completed."

clear :
	@echo "Cleaning up DB files..."
	rm -f *.sqlite3
	find ./api/migrations ! -name '__init__.py' -type f -exec rm -f {} +
	@echo "Cleanup completed."