VENV := . venv/bin/activate &&
TAG := $(shell git describe --tags --abbrev=0)
VERSION ?= $(shell git describe --tags --always)

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

publish: install publish-package publish-image

publish-package:
	rm -rdf dist
	$(MAKE) build
ifdef DRY_RUN
	$(VENV) python -m twine upload --repository testpypi dist/*
else
	$(VENV) python -m twine upload dist/*
endif

publish-image: login-ghcr
ifdef CI
	docker buildx build \
		-t ghcr.io/echohello-dev/transcribe-me:latest \
		-t ghcr.io/echohello-dev/transcribe-me:$(VERSION) \
		--cache-from=type=gha,scope=image \
		--cache-to=type=gha,mode=max \
		--platform $(DOCKER_DEFAULT_PLATFORM) \
		--push .
else
	docker compose build --push
endif

transcribe: install
	$(VENV) python -m transcribe_me.main

transcribe-archive: install
	$(VENV) python -m transcribe_me.main archive

transcribe-install: install
	$(VENV) python -m transcribe_me.main install

release-version:
ifdef CI
	git config --global user.email "actions@github.com"
	git config --global user.name "GitHub Actions"
endif
	git tag -a "v$(VERSION)"
	git push origin main
	git push --tags