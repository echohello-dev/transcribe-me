VENV := . venv/bin/activate &&


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
	asdf install
endif
	python3 -m venv venv
	$(VENV) pip install -r requirements.txt

install-cli: check-ffmpeg
	pip install .

test:
	python -m unittest discover -s tests

transcribe: install check-ffmpeg
	$(VENV) python transcribe_me/main.py

transcribe-install: install check-ffmpeg
	$(VENV) python transcribe_me/main.py install