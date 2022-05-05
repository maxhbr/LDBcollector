TOPDIR  := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
SRCDIR   = $(TOPDIR)/data
JSONDB   = $(TOPDIR)/fedora-licenses.json

# Paths
DESTDIR ?=
PREFIX  ?= /usr
DATADIR ?= /usr/share

all: validate json

validate: toml-validate spec-validate

toml-validate: $(SRCDIR)
	toml-validator $(SRCDIR)/*.toml

spec-validate: $(SRCDIR)
	$(TOPDIR)/tools/validate-spec.py $(SRCDIR)

json:
	$(TOPDIR)/tools/mkjson.py $(SRCDIR) $(JSONDB)

install:
	install -D -m 0644 $(JSONDB) $(DESTDIR)$(DATADIR)/rpminspect/licenses/$(shell basename $(JSONDB))

clean:
	-rm -f $(JSONDB)
