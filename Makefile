NAME= fly_in.py
PYTHON= poetry run python3
MYPY= poetry run mypy
FLAKE8= poetry run flake8
CONFIG_FILE=config.txt

.PHONY: install run debug lint lint-strict clean

install:
	@poetry install

run:
	@$(PYTHON) $(NAME) $(CONFIG_FILE)

debug:
	@$(PYTHON) -m pdb $(NAME) $(CONFIG_FILE)

lint:
	@$(FLAKE8) .
	@$(MYPY) . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	@$(FLAKE8) .
	@$(MYPY) . --strict

clean:
	rm -rf .__pycache__ .mypy__cache