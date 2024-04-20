VENV := . venv/bin/activate &&

-include .env
export


init:
	cp .env.example .env

check-ffmpeg:
ifeq (, $(shell which ffmpeg))
	$(error "No ffmpeg in PATH, please install ffmpeg")
else
	@echo "ffmpeg is installed"
endif

freeze:
	$(VENV) pip freeze > requirements.txt

login-ghcr:
ifdef GITHUB_TOKEN
	echo "${GITHUB_TOKEN}" | docker login ghcr.io -u "${GITHUB_ACTOR}" --password-stdin
endif

install:
ifneq (, $(shell which asdf))
	asdf install python
endif
	python3 -m venv venv
	$(VENV) pip install -r requirements.txt

install-cli: check-ffmpeg
	pip install .

test: install
	$(VENV) python -m unittest discover -s .

build: install
	$(VENV) python -m build

build-image:
	docker compose build
	VERSION=$(shell git describe --tags --abbrev=0) docker compose build

bump:
	$(VENV) python -m commitizen bump || $(VENV) python -m commitizen bump --increment patch

bump-major:
	$(VENV) python -m commitizen bump --increment major

bump-minor:
	$(VENV) python -m commitizen bump --increment minor

bump-patch:
	$(VENV) python -m commitizen bump --increment patch

gh-bump:
	gh workflow run version.yaml
	gh workflow view version.yaml --web

gh-publish-image:
	gh workflow run publish-image.yaml
	gh workflow view publish-image.yaml --web

publish-package:
	rm -rdf dist
	$(MAKE) build
ifdef DRY_RUN
	$(VENV) python -m twine upload --repository testpypi dist/*
else
	$(VENV) python -m twine upload dist/*
endif

publish-image: build-image login-ghcr
	docker compose push
	VERSION=$(shell git describe --tags --abbrev=0) docker compose push

transcribe: install
	$(VENV) python -m transcribe_me.main

transcribe-archive: install
	$(VENV) python -m transcribe_me.main archive

transcribe-install: install
	$(VENV) python -m transcribe_me.main install