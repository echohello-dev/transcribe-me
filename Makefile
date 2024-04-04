VENV := . venv/bin/activate &&

freeze:
	$(VENV) pip freeze > requirements.txt

install:
	python3 -m venv venv
	$(VENV) pip install -r requirements.txt

transcribe: install
	$(VENV) python transcribe_me/main.py

install-cli:
	pip install .