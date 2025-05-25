.PHONY: build

VENV := . venv/bin/activate &&
TAG := $(shell git describe --tags --abbrev=0)
VERSION ?= $(shell git describe --tags --always)

-include .env
export

init:
	cp .env.dev .env

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

test: install-test
	$(VENV) python -m pytest tests/unit -v --cov=transcribe_me --cov-report=term-missing

install-test:
	$(VENV) pip install -e ".[test]"

build:
	rm -rdf build dist
	$(VENV) python -m build

build-image:
	docker compose build

publish: publish-package publish-image

publish-package: install
	rm -rdf dist
	$(MAKE) build
	$(VENV) python -m twine check dist/*
ifdef DRY_RUN
	$(VENV) python -m twine upload --repository testpypi dist/*
else
	$(VENV) python -m twine upload dist/*
endif

publish-image: install login-ghcr
ifdef CI
	docker buildx build \
		-t ghcr.io/echohello-dev/transcribe-me:latest \
		-t ghcr.io/echohello-dev/transcribe-me:$(VERSION) \
		--cache-to "type=gha,mode=max" \
		--cache-from type=gha \
		--platform $(DOCKER_DEFAULT_PLATFORM) \
		--push \
		.
else
	docker compose build --push
endif

transcribe:
	$(VENV) python -m transcribe_me.main

transcribe-archive:
	$(VENV) python -m transcribe_me.main archive

transcribe-install:
	$(VENV) python -m transcribe_me.main install

release-version:
ifdef CI
	git config --global user.email "actions@github.com"
	git config --global user.name "GitHub Actions"
endif
	git tag -a "v$(VERSION)"
	git push origin main
	git push --tags