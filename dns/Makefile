all: venv/install

venv: ## Set up virtualenv
	python3 -m venv venv

venv/install: venv requirements.txt ## Install packages in venv
	./venv/bin/pip3 install -r requirements.txt
	touch venv/install

clean:
	rm -rf venv
