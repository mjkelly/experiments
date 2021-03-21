all: venv/install  ## [default] Set up local environment

venv: ## Create virtualenv
	python3 -m venv venv

venv/install: venv requirements.txt ## Install packages in venv.
	./venv/bin/python3 -m pip install -r requirements.txt
	touch venv/install

clean: ## Clean up local environment.
	rm -rf cloudinit-lvm
	rm -rf *.pyz
	rm -rf venv

cloudinit-lvm.pyz:  ## Make a mostly self-contained executable (needs python3)
	mkdir -p cloudinit-lvm
	python3 -m pip install -r requirements.txt --target cloudinit-lvm
	cp cloudinit-lvm.py cloudinit-lvm/__main__.py
	python3 -m zipapp -p "/usr/bin/env python3" cloudinit-lvm

.PHONY: help
help:  ## Show this help.
	@# From: https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
	@grep -E '^[a-zA-Z_/\.-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

