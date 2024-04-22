NAME=check_modulemd
INSTALLPATH=/usr/share/$(NAME)
PYTHONSITE=/usr/lib/python2.7/site-packages

all: install check

check:
	cd examples/testing-module; make

.PHONY: clean

clean:
	@python setup.py clean
	git clean -fd
	rm -rf build/html

install: clean
	@python setup.py install

source: clean
	@python setup.py sdist

help:
	@echo "Usage: make <target>"
	@echo
	@echo "Available targets are:"
	@echo " help                    show this text"
	@echo " clean                   remove python bytecode and temp files"
	@echo " install                 install program on current system"
	@echo " source                  create source tarball"
	@echo " check                   run examples/testing_module check target in Makefile"
