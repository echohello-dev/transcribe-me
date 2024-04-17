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

install:
ifneq (, $(shell which asdf))
	asdf install python
endif
	python3 -m venv venv
	$(VENV) pip install -r requirements.txt

install-cli: check-ffmpeg
	pip install .

test: install
	$(VENV) python -m unittest discover -s tests

build: install
	$(VENV) python -m build

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

publish: build
	rm -rdf dist
ifdef DRY_RUN
	$(VENV) python -m twine upload --repository testpypi dist/*
else
	$(VENV) python -m twine upload dist/*
endif

transcribe: install
	$(VENV) python transcribe_me/main.py

transcribe-archive: install
	$(VENV) python transcribe_me/main.py archive

transcribe-install: install
	$(VENV) python transcribe_me/main.py install