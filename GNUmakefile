
# CC_RDF_SOURCES := $(wildcard upstream/rdf/CC-*.rdf)
# CC_DATA_TARGETS := $(addprefix data/,$(notdir $(patsubst %.rdf,%.ttl,$(CC_RDF_SOURCES))))

# SOURCES := $(wildcard data/*.ttl) $(CC_DATA_TARGETS)
# RDF_TARGETS := $(addprefix www/id/,$(notdir $(patsubst %.ttl,%.rdf,$(SOURCES))))
# RDFA_TARGETS := $(addprefix www/id/,$(notdir $(patsubst %.ttl,%.html,$(SOURCES))))
# JSON_TARGETS := $(addprefix www/id/,$(notdir $(patsubst %.ttl,%.json,$(SOURCES))))
# JSONLD_TARGETS := $(addprefix www/id/,$(notdir $(patsubst %.ttl,%.jsonld,$(SOURCES))))



TXT_TARGETS := $(addprefix www/id/,$(notdir $(wildcard upstream/plaintext/*)))
JSON_TARGETS = $(patsubst %.ttl,%.json,$(wildcard www/id/*.ttl))
JSONLD_TARGETS = $(patsubst %.ttl,%.jsonld,$(wildcard www/id/*.ttl))

WEB_SOURCES = index.html license.html ns.html
WEB_VERBATIM = licensedb.css favicon.ico licensedb.png
WEB_TARGETS := $(addprefix www/,$(WEB_SOURCES) $(WEB_VERBATIM))

all: $(TXT_TARGETS) cc publish $(WEB_TARGETS)

jsonld: $(JSON_TARGETS) $(JSONLD_TARGETS) vocab
	@echo writing     www/context.json
	@cp data/context.json www/context.json

vocab:
	@echo serializing www/ns.jsonld
	@node_modules/.bin/turtle-to-jsonld data/vocab.ttl > www/ns.jsonld

website: $(WEB_TARGETS) | www
	@echo Generating id/index.html web page
	@php src/site/page.php src/site/id.php "../" > www/id/index.html


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

cc: src/build/turtle-cc.py
	mkdir --parents www/id
	@src/build/turtle-cc.py

publish: src/build/publish.py | txt
	mkdir --parents www/id
	@src/build/publish.py

website:

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

www/id/%.json: www/id/%.ttl www/context.json
	@echo Serializing to $@
	@node src/build/publish-json.js www/context.json $< $@

www/id/%.jsonld: www/id/%.json
	@cp $< $@

www/id/%.html: www/id/%.json data/context.json src/site/rdfa.php src/site/metadata.php
	@echo Serializing to $@
	@php src/site/rdfa.php $< > $@

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
