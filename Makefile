INIT =

.PHONY: migrate run clear

build :
	@echo "NOTE : You first need to set up a virtual environment."
	@echo "Building the project..."
	pip install -r requirements.txt
	@echo "Build completed."

migrate :
	@echo "Running database migrations..."
	python manage.py makemigrations
	python manage.py migrate
ifdef INIT
	@echo "Skipping super user creation."
else
	@echo "Initializing database with super user..."
	python manage.py createsuperuser
endif
	@echo "Database migrations completed."

run :
	@echo "Starting the development server..."
	python manage.py runserver

clear :
	@echo "Cleaning up DB files..."
	rm *.sqlite3
	find ./api/migrations ! -name '__init__.py' -type f -exec rm -f {} +
	@echo "Cleanup completed."