# Download rdfhdt from http://www.rdfhdt.org/download/ and then place a
# link to rdf2hdt in bin, e.g.:
#     ln -s ~/code/3rdparty/hdt-it/trunk/hdt-lib/tools/rdf2hdt bin/
RDF2HDT := bin/rdf2hdt

TODAY = `date +"%Y-%m-%d"`
TXT_TARGETS := $(addprefix www/id/,$(notdir $(wildcard upstream/plaintext/*)))
HTML_TARGETS = $(patsubst %.ttl,%.html,$(wildcard www/id/*.ttl))
JSONLD_TARGETS = $(patsubst %.ttl,%.jsonld,$(wildcard www/id/*.ttl))

WEB_SOURCES = index.html license.html ns.html
WEB_VERBATIM = licensedb.css favicon.ico licensedb.png
WEB_TARGETS := $(addprefix www/,$(WEB_SOURCES) $(WEB_VERBATIM))

all: $(TXT_TARGETS) cc publish dataset jsonld html website

jsonld: $(JSON_TARGETS) $(JSONLD_TARGETS) vocab

www/context.jsonld:
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

dataset: cc publish
	@src/build/combine.py
	rapper -i turtle www/dl/licensedb.ttl > www/dl/licensedb.nt
	$(RDF2HDT) -f ntriples www/dl/licensedb.nt www/dl/licensedb.hdt
	mv www/dl/licensedb.ttl www/dl/licensedb.$(TODAY).ttl
	mv www/dl/licensedb.hdt www/dl/licensedb.$(TODAY).hdt
	rm www/dl/licensedb.nt
	cat etc/ldf-server.template.json | sed "s/%DATE%/$(TODAY)/" > etc/ldf-server.json

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
	rm -rf www
