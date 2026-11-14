# One target per CI step; `make check` runs them all. Python 3.10 or newer, standard library only.
PYTHON ?= python3

.PHONY: check consistency test
check: consistency test

consistency:
	$(PYTHON) scripts/check.py

test:
	$(PYTHON) -m unittest discover -s tests -v
