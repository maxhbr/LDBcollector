SOURCES := $(wildcard data/*.turtle)
RDF_TARGETS := $(addprefix www/id/,$(notdir $(patsubst %.turtle,%.rdf,$(SOURCES))))
RDFA_TARGETS := $(addprefix www/id/,$(notdir $(patsubst %.turtle,%.html,$(SOURCES))))
JSON_TARGETS := $(addprefix www/id/,$(notdir $(patsubst %.turtle,%.json,$(SOURCES))))
JSONLD_TARGETS := $(addprefix www/id/,$(notdir $(patsubst %.turtle,%.jsonld,$(SOURCES))))

WEB_SOURCES = index.html license.html ns.html
WEB_VERBATIM = robots.txt favicon.ico licensedb.png
WEB_TARGETS := $(addprefix www/,$(WEB_SOURCES) $(WEB_VERBATIM)) www/id/index.html www/jquery.js

all: $(WEB_TARGETS) $(JSON_TARGETS) $(JSONLD_TARGETS) $(RDF_TARGETS) $(RDFA_TARGETS) www/dl/license-database.tar.gz

node_modules:
	npm install

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

www/context.json: data/context.json | www
	@cp $< $@ 

.build/%.nt: data/%.turtle | .build
	@echo Serializing to $@
	@rdf serialize $< > $@
	@if [ -s upstream/rdf/$(basename $(notdir $<)).rdf ]; then \
	    rdf serialize upstream/rdf/$(basename $(notdir $<)).rdf \
	    | ruby src/data/normalize.rb >> $@; \
	fi

www/dl/license-database.tar.gz: $(JSON_TARGETS) $(RDF_TARGETS) | www .build
	@echo Generating database archive $@
	@cp data/copyright.txt .build/license-database/
	@cp data/context.json .build/license-database/
	@cp www/id/*json .build/license-database/json/
	@cp www/id/*rdf .build/license-database/rdf/
	@cp upstream/plaintext/*txt .build/license-database/plaintext/
	@cd .build ; tar cfz ../www/dl/license-database.tar.gz license-database

www/id/%.json: .build/%.nt www/context.json | www node_modules
	@echo Serializing to $@
	@node src/build/publish-json.js www/context.json $< $@

www/id/%.jsonld: www/id/%.json
	@cp $< $@

www/id/%.rdf: .build/%.nt www/context.json | www
	@echo Serializing to $@
	@cd www/id ; ../../src/build/publish-rdf.rb ../../$<  ../../$@ ../context.json

www/id/%.html: www/id/%.json data/context.json src/site/rdfa.php src/site/metadata.php
	@echo Serializing to $@
	@php src/site/rdfa.php $< > $@

www/id/index.html: src/site/dbindex.php src/site/page.php $(SOURCES) | www  .build
	@echo Generating index at $@
	@php src/site/dbindex.php > .build/indexpage.html
	@php src/site/page.php .build/indexpage.html > $@

www/%.html: src/site/%.html src/site/page.php | www
	@echo Generating $@ web page 
	@php src/site/page.php $< > $@

www/robots.txt: src/site/robots.txt | www; @cp $< $@
www/favicon.ico: src/site/favicon.ico | www; @cp $< $@
www/licensedb.png: src/site/licensedb.png | www; @cp $< $@
www/jquery.js: upstream/jquery/jquery-1.7.1.min.js | www; @cp $< $@

clean:
	rm -rf .build
	rm -rf www
