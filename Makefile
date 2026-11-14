PYTHON ?= python3
.PHONY: test help
help:
	@printf 'make test          Run standard-library unit tests\n'
	@printf 'python3 tools/rg_batch.py --help   Explain GFA evidence pipeline\n'
test:
	$(PYTHON) -m unittest discover -s tests -v
