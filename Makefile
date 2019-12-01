help:
	@echo "Please use \`make <ROOT>' where <ROOT> is one of"
	@echo "  dependencies         to install project dependencies"
	@echo "  test                 to run tests"

test: **/*.py
	python3 -m unittest discover

dependencies:
	pip install -r requirements.txt
