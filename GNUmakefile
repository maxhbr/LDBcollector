SOURCES := $(wildcard data/*.turtle)
JSON_TARGETS := $(addprefix www/id/,$(notdir $(patsubst %.turtle,%.json,$(SOURCES))))
RDF_TARGETS := $(addprefix www/id/,$(notdir $(patsubst %.turtle,%.rdf,$(SOURCES))))

all: $(JSON_TARGETS) $(RDF_TARGETS)

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

.build/%.triples: data/%.turtle | .build
	@echo Serializing to $@
	@rdf serialize $< > $@
	@if [ -s upstream/rdf/$(basename $(notdir $<)).rdf ]; then \
	    rdf serialize upstream/rdf/$(basename $(notdir $<)).rdf >> $@; \
	fi

www/id/%.json: .build/%.triples www/context.json | www/id
	@echo Serializing to $@
	@cd www/id ; ../../build/publish-json.rb ../../$<  ../../$@ ../context.json

www/id/%.rdf: .build/%.triples www/context.json | www/id
	@echo Serializing to $@
	@cd www/id ; ../../build/publish-rdf.rb ../../$<  ../../$@ ../context.json

clean:
	rm -rf .build
	rm -rf www
