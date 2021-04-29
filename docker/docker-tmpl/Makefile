all: venv venv/install

venv:
	python3 -m venv venv

venv/install: requirements.txt
	./venv/bin/pip3 install -r requirements.txt
	cp requirements.txt venv/install

clean:
	rm -rf ./venv
