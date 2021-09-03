.PHONY: black
black:
	python -m black . --line-length=79

.PHONY: lint
lint:
	for package in configerus/*; do \
	    if [ -d "$$package" ]; then echo "$$package"; pylint -d duplicate-code -d pointless-string-statement -d import-error $$package; fi; \
	done
	for package in configerus/contrib/*; do \
	    if [ -d "$$package" ]; then echo "$$package"; pylint -d duplicate-code -d pointless-string-statement -d import-error $$package; fi; \
	done

.PHONY: clean
clean:
	rm -rf build dist *.log *.egg-info

build:
	python -m build

.PHONY: push
push:
	python -m twine upload dist/*
