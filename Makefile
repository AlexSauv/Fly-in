NAME= fly_in.py
PY= python3
MYPY= mypy
FLAKE8= flake8
PYDANTIC = pydantic
ARCADE = arcade

.PHONY: install run debug lint lint-strict clean clean-strict

install:
	$(PY) -m venv venv
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install -r requirements.txt	

run:
	@if [ ! -f ./venv/bin/python3 ]; then \
			echo "ERROR VENV: make sure to run 'make install' before 'make run' and to be in environment"; \
			exit 1; \
	fi
	./venv/bin/$(PY) $(NAME) $(ARGS)

debug:
	./venv/bin/$(PY) -m pdb $(NAME) $(ARGS)

clean:
	rm -rf __pycache__ .mypy_cache

clean-strict: clean
	rm -rf venv

lint:
	@./venv/bin/$(FLAKE8) . --exclude=venv
	@./venv/bin/$(MYPY) . --exclude=venv --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	@./venv/bin/$(FLAKE8) . --exclude=venv
	@./venv/bin/$(MYPY) . --exclude=venv --strict