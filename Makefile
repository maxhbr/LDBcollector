SRCDIRS = approved approved-content approved-documentation approved-fonts not-approved

all:

validate: $(SRCDIRS)
	toml-validator approved/*.toml
	toml-validator approved-content/*.toml
	toml-validator approved-documentation/*.toml
	toml-validator approved-fonts/*.toml
	toml-validator not-approved/*.toml
