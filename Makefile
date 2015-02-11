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

.PHONY : clean
clean:
	-find ./pyrename -type f -name \*.pyc | xargs -I xxx rm xxx
	-find ./pyrename -type d -name __pycache__ | xargs -I xxx rm -rf xxx
