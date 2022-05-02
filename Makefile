TOPDIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
SRCDIR  = $(TOPDIR)/data
JSONDB  = $(TOPDIR)/fedora-licenses.json

all: validate json

validate: toml-validate spec-validate

toml-validate: $(SRCDIR)
	toml-validator $(SRCDIR)/*.toml

spec-validate: $(SRCDIR)
	$(TOPDIR)/tools/validate-spec.py $(SRCDIR)

json:
	$(TOPDIR)/tools/mkjson.py $(SRCDIR) $(JSONDB)

clean:
	-rm -f $(JSONDB)
