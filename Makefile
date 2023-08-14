

test:
	PYTHONPATH=./python/ pytest --log-cli-level=10 tests/python/

check_license_files:
	# all JSON files should have a LICENSE file
	@for lf in `find licenses -name "*.json"`; \
		do LICENSE_FILE=`echo $$lf | sed 's/\.json/\.LICENSE/g'` ; \
			echo -n "$$lf -> $$LICENSE_FILE: " ; \
		   	ls $$LICENSE_FILE > /dev/null || (echo FAIL; exit 1) ; \
			echo "OK" ; \
	done

check: check_license_files

