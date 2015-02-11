VERB = 0
NOSE = nosetests --nologcapture --verbosity ${VERB}

help:
	@echo "[targets]"
	@echo "  tests"
	@echo "  help"

.PHONY : test
test: tests

.PHONY : tests
tests:
	${NOSE} -w ./pyrename/tests/

.PHONY : bin
bin: clean
	mkdir ./bin
	echo "#!/bin/bash" > ./bin/pyrename
	echo "export PYTHONPATH=$$PYTHONPATH:${CURDIR}" >> ./bin/pyrename
	echo "python3 -m pyrename.apps.main $$*" >> ./bin/pyrename
	chmod +x ./bin/pyrename

.PHONY : clean
clean:
	-find ./pyrename -type f -name \*.pyc | xargs -I xxx rm xxx
	-find ./pyrename -type d -name __pycache__ | xargs -I xxx rm -rf xxx
	-rm -rf ./bin
