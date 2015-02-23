
TXT_TARGETS := $(addprefix www/id/,$(notdir $(wildcard upstream/plaintext/*)))
HTML_TARGETS = $(patsubst %.ttl,%.html,$(wildcard www/id/*.ttl))
JSONLD_TARGETS = $(patsubst %.ttl,%.jsonld,$(wildcard www/id/*.ttl))

WEB_SOURCES = index.html license.html ns.html
WEB_VERBATIM = licensedb.css favicon.ico licensedb.png
WEB_TARGETS := $(addprefix www/,$(WEB_SOURCES) $(WEB_VERBATIM))

all: $(TXT_TARGETS) cc publish jsonld html website

jsonld: $(JSON_TARGETS) $(JSONLD_TARGETS) vocab
	@echo writing     www/context.jsonld
	@cp data/context.jsonld www/context.jsonld

html: $(HTML_TARGETS) $(JSONLD_TARGETS)

vocab:
	@echo writing     www/ns.ttl
	@cp data/vocab.ttl www/ns.ttl
	@echo serializing www/ns.jsonld
	@node_modules/.bin/turtle-to-jsonld data/vocab.ttl > www/ns.jsonld

website: $(WEB_TARGETS) | www
	@echo Generating id/index.html web page
	@php src/site/page.php src/site/id.php "../" > www/id/index.html

txt: $(TXT_TARGETS)

www:
	mkdir --parents www/id
	mkdir --parents www/dl

upstream:
	mkdir --parents upstream/plaintext
	mkdir --parents upstream/rdf
	src/build/plaintext-gnu.sh
	src/build/plaintext-cc.sh
	src/build/plaintext-odc.sh
	src/build/rdf-gnu.sh
	src/build/rdf-cc.sh

cc: src/build/turtle-cc.py
	mkdir --parents www/id
	@src/build/turtle-cc.py

publish: src/build/publish.py | txt
	mkdir --parents www/id
	@src/build/publish.py

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

www/id/%.jsonld: www/id/%.ttl www/context.jsonld
	@echo Serializing to $@
	@node src/build/publish-json.js www/context.jsonld $< $@

www/id/%.html: www/id/%.jsonld data/context.jsonld src/site/license-page.php src/site/metadata.php
	@echo Serializing to $@
	@php src/site/license-page.php $< > $@

www/%.html: src/site/%.html src/site/page.php vocab | www
	@echo Generating $@ web page
	@php src/site/page.php $< "" > $@

www/favicon.ico: src/site/favicon.ico | www; @cp $< $@
www/licensedb.png: src/site/licensedb.png | www; @cp $< $@
www/licensedb.css: src/site/licensedb.css | www; @cp $< $@

clean:
	rm -rf .build
	rm -rf www

deploy: | all
	@echo Deploying www to production.www
	test -x production.www && mv production.www production.old || true
	mv www production.www
	rm -rf production.old
