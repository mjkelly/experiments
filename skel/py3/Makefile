.DEFAULT_GOAL := venv/install

venv: ## Set up virtualenv
	python3 -m venv venv

venv/install: venv requirements.txt ## [default] Install packages in venv.
	./venv/bin/pip3 install -r requirements.txt
	touch venv/install

clean: ## Clean up local environment.
	rm -rf venv

.PHONY: help
help:  ## Show this help.
	@# From: https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
	@grep -E '^[a-zA-Z_-/]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
