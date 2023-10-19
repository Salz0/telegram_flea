.PHONY: env
env:
	poetry install

.PHONY: migrate
migrate:
	poetry run aerich upgrade

.PHONY: extract-locales
extract-locales:
	poetry run pybabel extract --input-dirs . --output ./locales/messages.pot

.PHONY: compile-locales
compile-locales:
	poetry run pybabel compile --directory ./locales

.PHONY: create-heroku-app
create-heroku-app:
	heroku apps:create --region eu telegram-flea

.PHONY: style
style:
	poetry run black .
	poetry run isort .
	poetry run pylint .
	poetry run pydocstyle .

.PHONY: setup
setup:
# Echo the command to be executed, with some information about the command itself.
	echo "Creating virtual environment and installing dependencies..."
	make env
	echo "Applying migrations..."
	make migrate
	echo "Extracting locales..."
	make extract-locales
	echo "Initializing a language: en"
	poetry run pybabel init -i locales/messages.pot -d locales -D messages -l en
	echo "Compiling locales..."
	make compile-locales
	echo "Applying style..."
	make style

.PHONY: run
run:
	poetry run python ./main.py
