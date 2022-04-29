TOPDIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
SRCDIR  = $(TOPDIR)/data

all:

validate: toml-validate spec-validate

toml-validate: $(SRCDIR)
	toml-validator $(SRCDIR)/*.toml

spec-validate: $(SRCDIR)
	$(TOPDIR)/tools/validate-spec.py $(SRCDIR)
