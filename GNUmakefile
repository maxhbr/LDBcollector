
TXT_TARGETS := $(addprefix www/id/,$(notdir $(wildcard upstream/plaintext/*)))

WEB_SOURCES = index.html license.html ns.html
WEB_VERBATIM = licensedb.css favicon.ico licensedb.png
WEB_TARGETS := $(addprefix www/,$(WEB_SOURCES) $(WEB_VERBATIM)) www/id/index.html www/jquery.js

all: $(TXT_TARGETS) cc publish $(WEB_TARGETS)

web: $(WEB_TARGETS)
txt: $(TXT_TARGETS)

node_modules:
	npm install

test:
	npm test

www:
	mkdir --parents www/id
	mkdir --parents www/dl

.build:
	mkdir --parents .build/license-database/json
	mkdir --parents .build/license-database/rdf
	mkdir --parents .build/license-database/plaintext

upstream:
	mkdir --parents upstream/plaintext
	mkdir --parents upstream/rdf
	src/build/plaintext-gnu.sh
	src/build/plaintext-cc.sh
	src/build/plaintext-odc.sh
	src/build/rdf-gnu.sh
	src/build/rdf-cc.sh

cc: src/build/turtle-cc.py | upstream
	mkdir --parents generated
	@src/build/turtle-cc.py

publish: src/build/publish.py | txt
	mkdir --parents generated
	@src/build/publish.py

www/context.json: data/context.json | www
	@cp $< $@

# .build/%.nt: data/%.turtle | .build
# 	@echo Serializing to $@
# 	@rapper --quiet --input turtle --output ntriples $< > $@.tmp
# 	@if [ -s upstream/rdf/$(basename $(notdir $<)).rdf ]; then \
# 	    rapper --quiet --input rdfxml --output ntriples upstream/rdf/$(basename $(notdir $<)).rdf \
# 	    | node src/build/normalize.js --quiet >> $@.tmp; \
# 	fi
# 	@node src/build/derive.js --all < $@.tmp > $@
# 	@rm $@.tmp

# www/dl/license-database.tar.gz: $(JSON_TARGETS) $(RDF_TARGETS) | www .build
# 	@echo Generating database archive $@
# 	@cp data/copyright.txt .build/license-database/
# 	@cp data/context.json .build/license-database/
# 	@cp www/id/*json .build/license-database/json/
# 	@cp www/id/*rdf .build/license-database/rdf/
# 	@cp www/id/*txt .build/license-database/plaintext/
# 	@cd .build ; tar cfz ../www/dl/license-database.tar.gz license-database

www/id/%.txt: upstream/plaintext/%.txt | www
	@echo Copying plaintext license to $@
	@cp $< $@

# www/id/%.json: .build/%.nt www/context.json | www node_modules
# 	@echo Serializing to $@
# 	@node src/build/publish-json.js www/context.json $< $@

# www/id/%.jsonld: www/id/%.json
# 	@cp $< $@

# www/id/%.rdf: .build/%.nt www/context.json | www
# 	@echo Serializing to $@
# 	@node src/build/publish-rdf-with-rapper.js www/context.json $< | sh > $@

www/id/%.html: www/id/%.json data/context.json src/site/rdfa.php src/site/metadata.php
	@echo Serializing to $@
	@php src/site/rdfa.php $< > $@

www/id/index.html: src/site/dbindex.php src/site/page.php $(JSON_TARGETS) | www  .build
	@echo Generating index at $@
	@php src/site/dbindex.php > .build/indexpage.html
	@php src/site/page.php .build/indexpage.html "../" > $@

www/%.html: src/site/%.html src/site/page.php | www
	@echo Generating $@ web page
	@php src/site/page.php $< "" > $@

www/favicon.ico: src/site/favicon.ico | www; @cp $< $@
www/licensedb.png: src/site/licensedb.png | www; @cp $< $@
www/licensedb.css: src/site/licensedb.css | www; @cp $< $@
www/jquery.js: upstream/jquery/jquery-1.7.1.min.js | www; @cp $< $@

clean:
	rm -rf generated/
	rm -rf .build
	rm -rf www

deploy: | all
	@echo Deploying www to production.www
	test -x production.www && mv production.www production.old || true
	mv www production.www
	rm -rf production.old
