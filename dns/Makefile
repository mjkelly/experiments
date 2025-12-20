all: venv/install

venv: ## Set up virtualenv
	python3 -m venv venv

venv/install: venv requirements.txt ## Install packages in venv
	./venv/bin/pip3 install -r requirements.txt
	touch venv/install

clean:
	rm -rf venv

typecheck: venv/typecheck ## Run type checks
	./venv/bin/mypy route53-update2.py

venv/typecheck: venv/install ## Prepare for type checking
	./venv/bin/pip3 install mypy
	touch venv/typecheck
	
.PHONY: all clean typecheck