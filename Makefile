VENV := . venv/bin/activate &&


freeze:
	$(VENV) pip freeze > requirements.txt

install:
ifeq (, $(shell which ffmpeg))
	$(error "No ffmpeg in PATH, please install ffmpeg")
endif
ifneq (, $(shell which asdf))
	asdf install
endif
	python3 -m venv venv
	$(VENV) pip install -r requirements.txt

transcribe: install
	$(VENV) python transcribe_me/main.py

transcribe-install: install
	$(VENV) python transcribe_me/main.py install

install-cli:
	pip install .