# SPDX-FileCopyrightText: 2023 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later


check: license python clean check-reuse build
	@echo "\n\n\n   Yay.... check succeeded :)\n\n\n"

check_license_files:

# all JSON files should have a LICENSE file
	@for lf in `find var/licenses -name "*.json" | grep -v -e compounds.json -e duals.json -e ambiguities.json`; \
		do \
			LICENSE_FILE=`echo $$lf | sed 's/\.json/\.LICENSE/g'` ; \
			echo "$$lf";\
			echo -n " * $$LICENSE_FILE: " ; \
		   	ls $$LICENSE_FILE > /dev/null || (echo FAIL; exit 1) &&  \
			echo "OK" && \
			echo -n " * JSON: " && jq . $$lf > /dev/null || exit 1 &&  \
			echo "OK" ; \
	done

# all LICENSE files should have a JSON file
	@for lf in `find var/licenses -name "*.LICENSE"`; \
		do JSON_FILE=`echo $$lf | sed 's/\.LICENSE/\.json/g'` ; \
			echo -n "$$lf -> $$JSON_FILE: " ; \
		   	ls $$JSON_FILE > /dev/null || exit 1 ; \
			echo "OK" ; \
	done

# Make sure schema is valid JSON
	@echo -n "License schema: " ; \
		   	jq . var/license_schema.json > /dev/null || exit 1 ; \
			echo "OK" ;

# Sanity check the content
	@echo -m "Sanity check the licenses: " ; \
		./tests/shell/sanity-check.sh || exit 1; echo "OK"

# Check disclaimers
	@echo -m "Check the disclaimers: " ; \
		./tests/shell/check-disclaimer.sh || exit 1; echo "OK"

# check JSON file not being licenses
	@for lf in `find var/  -maxdepth 1  -name "*.json" `; \
		do \
		echo -n "$$lf " ; \
	 	jq . $$lf > /dev/null || exit 1 ; \
		echo "OK" ; \
	done

check_license_schema:
# the py tool has an option "--check" that checks every license against license schema
# check one license, e.g. mpl, to check 'em all
	@echo -n "Use py command to check licenses against schema: " ; \
		   	PYTHONPATH=python python/flame/__main__.py --check license mpl-2.0  > /dev/null || exit 1 ; \
			echo "OK" ; 

check_schema:
# check the license schema
	@echo -n "Make sure schema is in valid JSON: " 
	@jq . var/license_schema.json > /dev/null 
	@echo "OK" ; 


check-reuse: clean
	reuse --suppress-deprecation lint

lint: check-reuse py-lint

license: check_schema check_license_files check-py-cli check_license_schema

.PHONY: python check-py-cli
python: py-test py-sort py-lint check-py-cli py-doctest py-doc

py-doctest:
	@cd python && python3 -m doctest -v flame/license_db.py 
	@cd python && python3 -m doctest -v flame/format.py 

py-test:
	PYTHONPATH=python/ python3 -m pytest --log-cli-level=10 tests/python/

py-sort:
	cd python && isort ./*/*.py --diff

py-lint:
	cd python && PYTHONPATH=. flake8 flame

py-doc:
#cd python/docs && PYTHONPATH=. make html
	cd python && rm -fr docs/build && PYTHONPATH=. sphinx-build -E docs/source/ docs/build/html


check-py-cli:
	@echo -n "Check cli (-h): "
	@PYTHONPATH=./python python3 ./python/flame/__main__.py -h > /dev/null
	@echo "OK"

	@echo -n "Check cli (alias): "
	@PYTHONPATH=./python python3 ./python/flame/__main__.py license "BSD3 and BSD3" > /dev/null
	@echo "OK"

	@echo -n "Check cli (compat): "
	@PYTHONPATH=./python python3 ./python/flame/__main__.py -of json compat x11-keith-packard > /dev/null
	@echo "OK"

doc: py-doc

build:
	cd python && rm -fr build && python3 setup.py sdist
	cd python && if [ `tar ztvf dist/*.tar.gz | grep -e LICENSES/GPL-3.0-or-later.txt -e requirements.txt -e licenses/ZPL-1.1.json | wc -l` -ne 3 ] ; then echo "Check for files in the tar.gz failed...."; exit 3; fi
	@echo
	@echo "build ready :)"

py-release: check clean build
	./devel/check-release.sh
	@echo
	@echo "To upload: "
	@echo "twine upload --repository foss-flame --verbose  dist/*"

stats:
	@echo -n "licenses:     "
	@PYTHONPATH=./python ./python/flame/__main__.py licenses | wc -l
	@echo -n "aliases:      "
	@PYTHONPATH=./python ./python/flame/__main__.py aliases | wc -l
	@echo -n "compats:      "
	@PYTHONPATH=./python ./python/flame/__main__.py compats | wc -l
	@echo -n "operators:    "
	@PYTHONPATH=./python ./python/flame/__main__.py operators | wc -l
	@echo -n "ambiguities:  "
	@PYTHONPATH=./python ./python/flame/__main__.py ambiguities | wc -l
	@echo -n "compounds:    "
	@PYTHONPATH=./python ./python/flame/__main__.py compounds | wc -l

clean:
	find . -name "*~"    | xargs rm -fr
	find . -name "*.pyc" | xargs rm -fr
	find . -name ".#*" | xargs rm -fr
	rm -f .coverage
	rm -fr python/foss_flame.egg-info
	rm -fr python/*flame.egg*
	rm -fr python/dist
	rm -fr python/build
	rm -fr python/docs/build
