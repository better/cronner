.PHONY: test build-assets publish-assets clean

test:
	python3 -m venv --clear venv
	venv/bin/python setup.py test

build-assets:
	rm -rf dist/
	python3 -m venv --clear venv
	venv/bin/python setup.py sdist
	venv/bin/pip install wheel
	venv/bin/python setup.py bdist_wheel --universal

publish-assets:
	make build-assets
	venv/bin/pip install twine
	venv/bin/twine upload dist/*

clean:
	git clean -fdX
