TOPDIR  := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
SRCDIR   = $(TOPDIR)/data
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

install:
	install -D -m 0644 $(JSONDB) $(DESTDIR)$(DATADIR)/fedora-license-data/licenses/$(shell basename $(JSONDB))
	install -D -m 0644 $(RPMLINT_SPDX) $(DESTDIR)$(ETCDIR)/xdg/rpmlint/$(shell basename $(RPMLINT_SPDX))
	install -D -m 0644 $(RPMLINT_LEGACY) $(DESTDIR)$(ETCDIR)/xdg/rpmlint/$(shell basename $(RPMLINT_LEGACY))

clean:
	-rm -f $(JSONDB)
