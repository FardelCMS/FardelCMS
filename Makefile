help:
	@echo "Please use \`make <ROOT>' where <ROOT> is one of"
	@echo "  dependencies         to install project dependencies"
	@echo "  test                 to run tests"

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf migrations/
	rm -rf uploads/
	rm -rf fardel.egg-info/
	rm -f manage.py

test: **/*.py
	python3 -m unittest discover

dependencies:
	pip install -r requirements.txt
