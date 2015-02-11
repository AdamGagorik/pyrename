VERB  = 0
NOSE  = nosetests --nologcapture --verbosity ${VERB}
BPATH = ${CURDIR}/bin
SPATH = ${BPATH}/pyrename

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
	mkdir ${BPATH}
	echo '#!/bin/bash' > ${SPATH}
	echo 'export PYTHONPATH=$$PYTHONPATH:${CURDIR}' >> ${SPATH}
	echo 'python3 -m pyrename.apps.main $$*' >> ${SPATH}
	chmod +x ${SPATH}

.PHONY : install
install: bin
	-mkdir -p ${HOME}/bin
	-rm ${HOME}/bin/pyrename
	ln -s ${SPATH} ${HOME}/bin/pyrename

.PHONY : clean
clean:
	-find ./pyrename -type f -name \*.pyc | xargs -I xxx rm xxx
	-find ./pyrename -type d -name __pycache__ | xargs -I xxx rm -rf xxx
	-rm -rf ./bin
