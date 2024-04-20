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
	python -m venv venv
	$(VENV) pip install -r requirements.txt

install-cli: check-ffmpeg
	pip install .

format:
	$(VENV) python -m black transcribe_me

lint:
	$(VENV) python -m pylint transcribe_me --fail-under 7

# TODO: $(VENV) python -m unittest discover -s .
test: install
	@echo "Not implemented"

build: install
	rm -rdf build dist
	$(VENV) python -m build

build-image:
	docker compose build

tag-release: install
	git branch --force -D release/$(shell git describe --tags --abbrev=0)
	git checkout -b release/$(shell git describe --tags --abbrev=0)
	git push --set-upstream origin release/$(shell git describe --tags --abbrev=0)
	git push --tags

bump-prerelease: install
	$(VENV) python -m commitizen bump --yes -pr alpha
	git push --tags

bump-major: install
	git checkout main
	git checkout -b release/$(shell git describe --tags --abbrev=0)
	$(VENV) python -m commitizen bump --yes --increment major
	git push --tags

bump-minor: install
	git checkout main
	git checkout -b release/$(shell git describe --tags --abbrev=0)
	$(VENV) python -m commitizen bump --yes --increment minor
	git push --tags

bump-patch: install
	git checkout main
	git checkout -b release/$(shell git describe --tags --abbrev=0)
	$(VENV) python -m commitizen bump --yes --increment patch
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