init:
	pip install -r requirements.txt

test:
	python3 -m unittest discover -s tests

coverage:
	coverage run -m unittest discover -s tests && coverage html && open htmlcov/index.html

.PHONY: init test