venv/bin/activate:
	python3 -m venv venv
	venv/bin/pip install pygame

run: venv/bin/activate
	venv/bin/python main.py