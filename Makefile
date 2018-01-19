.PHONY: test
test:
	python3 -m venv --clear venv
	venv/bin/python setup.py test

.PHONY: build-assets
build-assets:
	rm -rf dist/
	python3 -m venv --clear venv
	venv/bin/python setup.py sdist
	venv/bin/pip install wheel
	venv/bin/python setup.py bdist_wheel --universal

.PHONY: publish-assets
publish-assets:
	make build-assets
	venv/bin/pip install twine
	venv/bin/twine upload dist/*

.PHONY: clean
clean:
	rm -rf *.egg-info/ *.pyc __pycache__/ build/ dist/ venv/
