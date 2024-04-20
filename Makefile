VENV := . venv/bin/activate &&
LATEST_TAG := $(shell git describe --tags --abbrev=0)
LATEST_VERSION := $(shell git describe)

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

tag-release: install
	git branch --force -D release/$(LATEST_TAG)
	git checkout -b release/$(LATEST_TAG)
	git push --set-upstream origin release/$(LATEST_TAG)
	git push --tags

bump-prerelease: install
ifdef CI
	git config --global user.email "actions@github.com"
	git config --global user.name "GitHub Actions"
endif
	$(VENV) python -m commitizen bump --yes -pr alpha
	git push --tags

bump-major: install
	git checkout main
	git pull
	$(eval NEW_VERSION := $(shell echo $(LATEST_VERSION) | awk -F. '{printf("%d.%d.%d", $$1+1, 0, 0)}'))
	sed -i 's/version = "$(LATEST_VERSION)"/version = "$(NEW_VERSION)"/' pyproject.toml
	git add pyproject.toml
	git commit -m "Bump version to $(NEW_VERSION)"
	git tag -a "v$(NEW_VERSION)" -m "Release v$(NEW_VERSION)"
	git push origin main
	git push --tags

bump-minor: install
	git checkout main
	git pull
	$(eval NEW_VERSION := $(shell echo $(LATEST_VERSION) | awk -F. '{printf("%d.%d.%d", $$1, $$2+1, 0)}'))
	sed -i 's/version = "$(LATEST_VERSION)"/version = "$(NEW_VERSION)"/' pyproject.toml
	git add pyproject.toml
	git commit -m "Bump version to $(NEW_VERSION)"
	git tag -a "v$(NEW_VERSION)" -m "Release v$(NEW_VERSION)"
	git push origin main
	git push --tags

bump-patch: install
	git checkout main
	git pull
	$(eval NEW_VERSION := $(shell echo $(LATEST_VERSION) | awk -F. '{printf("%d.%d.%d", $$1, $$2, $$3+1)}'))
	sed -i 's/version = "$(LATEST_VERSION)"/version = "$(NEW_VERSION)"/' pyproject.toml
	git add pyproject.toml
	git commit -m "Bump version to $(NEW_VERSION)"
	git tag -a "v$(NEW_VERSION)" -m "Release v$(NEW_VERSION)"
	git push origin main
	git push --tags

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