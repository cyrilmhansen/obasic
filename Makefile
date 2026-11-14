PYTHON ?= python3
.PHONY: test help sources
help:
	@printf 'make test          Run standard-library unit tests\n'
	@printf 'make sources       List candidate historical artifacts\n'
	@printf 'python3 tools/rg_batch.py --help   Explain GFA evidence pipeline\n'
test:
	$(PYTHON) -m unittest discover -s tests -v

sources:
	$(PYTHON) tools/acquire.py list
