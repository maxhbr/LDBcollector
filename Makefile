# SPDX-FileCopyrightText: 2023 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later


check: license python clean check-reuse build
	@echo "\n\n\n   Yay.... check succeeded :)\n\n\n"

check_license_files:
# all JSON files should have a LICENSE file
	@for lf in `find var/licenses -name "*.json"`; \
		do \
			LICENSE_FILE=`echo $$lf | sed 's/\.json/\.LICENSE/g'` ; \
			echo "$$lf";\
			echo -n " * $$LICENSE_FILE: " ; \
		   	ls $$LICENSE_FILE > /dev/null || (echo FAIL; exit 1) &&  \
			echo "OK" && \
			echo -n " * JSON: " && jq . $$lf > /dev/null || (echo FAIL; exit 1) &&  \
			echo "OK" ; \
	done
# all LICENSE files should have a JSON file
	@for lf in `find var/licenses -name "*.LICENSE"`; \
		do JSON_FILE=`echo $$lf | sed 's/\.LICENSE/\.json/g'` ; \
			echo -n "$$lf -> $$JSON_FILE: " ; \
		   	ls $$JSON_FILE > /dev/null || (echo FAIL; exit 1) ; \
			echo "OK" ; \
	done
	@echo -n "License schema: " ; \
		   	jq . var/license_schema.json > /dev/null || (echo FAIL; exit 1) ; \
			echo "OK" ; \

check-reuse:
	reuse --suppress-deprecation lint

license: check_license_files 

.PHONY: python check-py-cli
python: py-test py-sort py-lint check-py-cli

py-test:
	PYTHONPATH=./python/ pytest --log-cli-level=10 tests/python/

py-sort:
	cd python && isort ./*/*.py --diff

py-lint:
	cd python && PYTHONPATH=. flake8

check-py-cli:
	@echo -n "Check cli (-h): "
	@PYTHONPATH=./python python3 ./python/flame/__main__.py -h > /dev/null
	@echo "OK"

	@echo -n "Check cli (alias): "
	@PYTHONPATH=./python python3 ./python/flame/__main__.py identify BSD3 > /dev/null
	@echo "OK"

	@echo -n "Check cli (compat): "
	@PYTHONPATH=./python python3 ./python/flame/__main__.py -of json compat x11-keith-packard > /dev/null
	@echo "OK"

build:
	cd python && rm -fr build && python3 setup.py sdist

clean:
	find . -name "*~"    | xargs rm -fr
	find . -name "*.pyc" | xargs rm -fr
	find . -name ".#*" | xargs rm -fr
	rm -f .coverage
	rm -fr python/flame.egg-info
	rm -fr python/dist
