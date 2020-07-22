.PHONY: clean data lint get_data

#################################################################################
# GLOBALS                                                                       #
#################################################################################

SHELL=/bin/bash
PROJECT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
BUCKET = [OPTIONAL] your-bucket-for-syncing-data (do not include 's3://')
PROFILE = default
PROJECT_NAME = craiglist_crawler
PYTHON_INTERPRETER = python
CONDA_ROOT=$(shell conda info --base)
ENV_NAME=craiglist_crawler
MY_ENV_DIR=$(CONDA_ROOT)/envs/$(ENV_NAME)

# conda activate does stuff other than just modifying path. This is a more complete way to run a
# a command in a conda env
# Note that the extra activate is needed to ensure that the activate floats env to the front of PATH
CONDA_ACTIVATE=source $$(conda info --base)/etc/profile.d/conda.sh ; conda activate ; conda activate


#################################################################################
# COMMANDS                                                                      #
#################################################################################

## Make Dataset
data: environment.yml
	$(PYTHON_INTERPRETER) src/data/make_dataset.py data/raw data/processed

## Delete all compiled Python files
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

## Lint using flake8
lint:
	flake8 src

## Download data from db
get_data: environment
	$(PYTHON_INTERPRETER) src/data/get_dataset.py

## Build Jupyter Environment
jupyter: environment
	$(MY_ENV_DIR)/bin/jupyter labextension install @jupyter-widgets/jupyterlab-manager
	$(MY_ENV_DIR)/bin/jupyter labextension install jupyterlab-plotly
	$(MY_ENV_DIR)/bin/jupyter labextension install plotlywidget
	$(MY_ENV_DIR)/bin/jupyter labextension install jupyterlab-theme-solarized-dark
	$(MY_ENV_DIR)/bin/jupyter lab build --name "craigslab"

## Set up python interpreter environment
environment: environment.yml
ifneq ("$(wildcard $(MY_ENV_DIR))","") # check if the directory is there
	conda env update $(ENV_NAME) --file environment.yml --prune
	ipython kernel install --name $(ENV_NAME) --user
else
	conda env create -f environment.yml
	ipython kernel install --name $(ENV_NAME) --user
endif
	@echo ">>> Conda env ${ENV_NAME) ready. Activate with:\nconda activate $(ENV_NAME)"
	touch environment # emtpy file which keeps track of when this rule was last run

environment.yml:

#################################################################################
# PROJECT RULES                                                                 #
#################################################################################



#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := help

# Inspired by <http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html>
# sed script explained:
# /^##/:
# 	* save line in hold space
# 	* purge line
# 	* Loop:
# 		* append newline + line to hold space
# 		* go to next line
# 		* if line starts with doc comment, strip comment character off and loop
# 	* remove target prerequisites
# 	* append hold space (+ newline) to line
# 	* replace newline plus comments by `---`
# 	* print line
# Separate expressions are necessary because labels cannot be delimited by
# semicolon; see <http://stackoverflow.com/a/11799865/1968>
.PHONY: help
help:
	@echo "$$(tput bold)Available rules:$$(tput sgr0)"
	@echo
	@sed -n -e "/^## / { \
		h; \
		s/.*//; \
		:doc" \
		-e "H; \
		n; \
		s/^## //; \
		t doc" \
		-e "s/:.*//; \
		G; \
		s/\\n## /---/; \
		s/\\n/ /g; \
		p; \
	}" ${MAKEFILE_LIST} \
	| LC_ALL='C' sort --ignore-case \
	| awk -F '---' \
		-v ncol=$$(tput cols) \
		-v indent=19 \
		-v col_on="$$(tput setaf 6)" \
		-v col_off="$$(tput sgr0)" \
	'{ \
		printf "%s%*s%s ", col_on, -indent, $$1, col_off; \
		n = split($$2, words, " "); \
		line_length = ncol - indent; \
		for (i = 1; i <= n; i++) { \
			line_length -= length(words[i]) + 1; \
			if (line_length <= 0) { \
				line_length = ncol - indent - length(words[i]) - 1; \
				printf "\n%*s ", -indent, " "; \
			} \
			printf "%s ", words[i]; \
		} \
		printf "\n"; \
	}' \
	| more $(shell test $(shell uname) = Darwin && echo '--no-init --raw-control-chars')
