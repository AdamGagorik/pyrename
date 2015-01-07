FNAME=pyrename.py
BPATH=${HOME}/bin
IPATH=${PWD}/${FNAME}
OPATH=${BPATH}/${FNAME}

help:
	@echo "[paths]"
	@echo "  BPATH : ${BPATH}"
	@echo "  IPATH : ${IPATH}"
	@echo "  OPATH : ${OPATH}"
	@echo ""
	@echo "[targets]"
	@echo "  clean"
	@echo "  copy"
	@echo "  link"
	@echo "  help"

copy: clean
	-cp ${IPATH} ${OPATH}

link: clean
	-ln -s ${IPATH} ${OPATH}

clean:
	-rm ${OPATH}
