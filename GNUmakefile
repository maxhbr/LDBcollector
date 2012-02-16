SOURCES := $(wildcard data/*.turtle)
JSON_TARGETS := $(addprefix www/id/,$(notdir $(patsubst %.turtle,%.json,$(SOURCES))))
RDFA_TARGETS := $(addprefix www/id/,$(notdir $(patsubst %.turtle,%.html,$(SOURCES))))
RDF_TARGETS := $(addprefix www/id/,$(notdir $(patsubst %.turtle,%.rdf,$(SOURCES))))

WEB_SOURCES = index.html license.html ns.html
WEB_VERBATIM = robots.txt favicon.ico licensedb.png
WEB_TARGETS := $(addprefix www/,$(WEB_SOURCES) $(WEB_VERBATIM)) www/id/index.html www/jquery.js

all: $(JSON_TARGETS) $(RDFA_TARGETS) $(RDF_TARGETS) $(WEB_TARGETS)

www/id:
	mkdir --parents www/id

.build:
	mkdir --parents .build

upstream:
	mkdir --parents upstream/plaintext
	mkdir --parents upstream/rdf
	build/plaintext-gnu.sh
	build/plaintext-cc.sh
	build/plaintext-odc.sh
	build/rdf-gnu.sh

www/context.json: data/context.json | www/id
	@cp $< $@ 

.build/%.nt: data/%.turtle | .build
	@echo Serializing to $@
	@rdf serialize $< > $@
	@if [ -s upstream/rdf/$(basename $(notdir $<)).rdf ]; then \
	    rdf serialize upstream/rdf/$(basename $(notdir $<)).rdf \
	    | ruby src/data/normalize.rb >> $@; \
	fi

www/id/%.json: .build/%.nt www/context.json | www/id
	@echo Serializing to $@
	@cd www/id ; ../../build/publish-json.rb ../../$<  ../../$@ ../context.json

www/id/%.rdf: .build/%.nt www/context.json | www/id
	@echo Serializing to $@
	@cd www/id ; ../../build/publish-rdf.rb ../../$<  ../../$@ ../context.json

www/id/%.html: www/id/%.json data/context.json src/site/rdfa.php src/site/metadata.php
	@echo Serializing to $@
	@php src/site/rdfa.php $< > $@

www/id/index.html: src/site/dbindex.php src/site/page.php $(SOURCES) | www/id  .build
	@echo Generating index at $@
	@php src/site/dbindex.php > .build/indexpage.html
	@php src/site/page.php .build/indexpage.html > $@

www/%.html: src/site/%.html src/site/page.php | www/id
	@echo Generating $@ web page 
	@php src/site/page.php $< > $@

www/robots.txt: src/site/robots.txt | www/id; @cp $< $@
www/favicon.ico: src/site/favicon.ico | www/id; @cp $< $@
www/licensedb.png: src/site/licensedb.png | www/id; @cp $< $@
www/jquery.js: upstream/jquery/jquery-1.7.1.min.js | www/id; @cp $< $@

clean:
	rm -rf .build
	rm -rf www
