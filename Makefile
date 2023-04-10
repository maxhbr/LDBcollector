TOPDIR  := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
SRCDIR   = $(TOPDIR)/data
GRAMMARDIR = $(TOPDIR)/grammar
JSONDB   = $(TOPDIR)/fedora-licenses.json
RPMLINT_SPDX = $(TOPDIR)/fedora-spdx-licenses.toml
RPMLINT_LEGACY = $(TOPDIR)/fedora-legacy-licenses.toml

# Paths
DESTDIR ?=
PREFIX  ?= /usr
DATADIR ?= /usr/share
ETCDIR ?= /etc

all: spec-validate json rpmlint

validate: toml-validate spec-validate

toml-validate: $(SRCDIR)
	toml-validator $(SRCDIR)/*.toml

spec-validate: $(SRCDIR)
	$(TOPDIR)/tools/validate-spec.py $(SRCDIR)

json:
	$(TOPDIR)/tools/mkjson.py $(SRCDIR) $(JSONDB)

rpmlint:
	$(TOPDIR)/tools/mkrpmlint.py $(SRCDIR) $(RPMLINT_SPDX) $(RPMLINT_LEGACY)

grammar: json
	$(GRAMMARDIR)/generate-spdx-ids.py $(JSONDB) > $(GRAMMARDIR)/fedora-spdx.txt
	$(GRAMMARDIR)/create-grammar.py $(GRAMMARDIR)/grammar.lark \
		$(GRAMMARDIR)/fedora-spdx.txt > $(GRAMMARDIR)/full-grammar.lark

install-grammar: grammar
	install -D -p $(GRAMMARDIR)/full-grammar.lark $(DESTDIR)$(DATADIR)/fedora-license-data/grammar.lark

install-rpmlint:
	install -D -p -m 0644 $(RPMLINT_SPDX) \
		$(DESTDIR)$(ETCDIR)/xdg/rpmlint/$(shell basename $(RPMLINT_SPDX))
	install -D -p -m 0644 $(RPMLINT_LEGACY) \
		$(DESTDIR)$(ETCDIR)/xdg/rpmlint/$(shell basename $(RPMLINT_LEGACY))

install-json:
	install -D -p -m 0644 $(JSONDB) \
		$(DESTDIR)$(DATADIR)/fedora-license-data/licenses/$(shell basename $(JSONDB))

install: install-json install-rpmlint install-grammar

check-grammar: grammar
	$(GRAMMARDIR)/test-grammar.py --file $(GRAMMARDIR)/full-grammar.lark

# this is not packaged. You may need
#  pip install check-jsonschema
# and add ~/.local/bin/check-jsonschema to your path
check-json:
	check-jsonschema --schemafile tools/fedora-license-schema.json fedora-licenses.json

legal-doc:
	$(TOPDIR)/tools/create-docs.py $(TOPDIR)/data

clean:
	-rm -f $(JSONDB)
