NAME= MapRendering.py
PY= python3
MYPY= mypy
FLAKE8= flake8
PYDANTIC = pydantic
ARCADE = arcade

.PHONY: install run debug lint lint-strict clean

install:
	python3 -m venv venv
	./venv/bin/pip install $(MYPY) $(FLAKE8) $(PYDANTIC) $(ARCADE)	

run:
	./venv/bin/$(PY) $(NAME) $(ARGS)

debug:
	./venv/bin/$(PY) -m pdb $(NAME) $(ARGS)

clean:
	rm -rf __pycache__ .mypy__cache

lint:
	@$(FLAKE8) .
	@$(MYPY) . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	@$(FLAKE8) .
	@$(MYPY) . --strict