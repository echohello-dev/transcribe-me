VENV := . venv/bin/activate &&
LATEST_TAG := $(shell git describe --tags --abbrev=0)
LATEST_VERSION := $(shell git describe --tags)

-include .env
export

define release_version =
ifdef CI
	git config --global user.email "actions@github.com"
	git config --global user.name "GitHub Actions"
endif
	sed -i '' "s/__version__ = '.*'/__version__ = '$(1)'/g" transcribe_me/__init__.py
	git add transcribe_me/__init__.py
	git commit -m "chore: Bump version to $(1)"
	git tag -a "v$(1)"
	git push origin main
	git push --tags
	git branch --force -D release/$(1)
	git checkout -b release/$(1)
	git push --set-upstream origin release/$(1)
endef

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
else
	$(warning "GITHUB_TOKEN is not set")
endif

install:
ifneq (, $(shell which asdf))
	asdf install python
endif
	python -m venv venv
	$(VENV) pip install -r requirements.txt

install-cli: check-ffmpeg
	pip install .

format:
	$(VENV) python -m black transcribe_me

lint:
	$(VENV) python -m pylint transcribe_me --fail-under 7

# TODO: $(VENV) python -m unittest discover -s .
test:
	@echo "Not implemented"

build:
	rm -rdf build dist
	$(VENV) python -m build

build-image:
	docker compose build

release-major:
	$(eval NEW_MAJOR_VERSION=$(shell echo "$(LATEST_TAG)" | awk -F'.' '{printf "%d.0.0", $$1 + 1}'))
	$(call release_version,$(NEW_MAJOR_VERSION))

release-minor:
	$(eval NEW_MINOR_VERSION=$(shell echo "$(LATEST_TAG)" | awk -F'.' '{printf "%d.%d.0", $$1, $$2 + 1}'))
	$(call release_version,$(NEW_MINOR_VERSION))

release-patch:
	$(eval NEW_PATCH_VERSION=$(shell echo "$(LATEST_TAG)" | awk -F'.' '{printf "%d.%d.%d", $$1, $$2, $$3 + 1}'))
	$(call release_version,$(NEW_PATCH_VERSION))

gh-publish-image:
	gh workflow view prerelease.yaml --web

publish-package:
	rm -rdf dist
	$(MAKE) build
ifdef DRY_RUN
	$(VENV) python -m twine upload --repository testpypi dist/*
else
	$(VENV) python -m twine upload dist/*
endif

publish-image: login-ghcr
	docker compose build --push

transcribe: install
	$(VENV) python -m transcribe_me.main

transcribe-archive: install
	$(VENV) python -m transcribe_me.main archive

transcribe-install: install
	$(VENV) python -m transcribe_me.main install