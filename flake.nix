{
  description = "ldbcollector in rust";

  inputs = {
    nixpkgs.url      = "github:NixOS/nixpkgs/nixpkgs-unstable";
    rust-overlay.url = "github:oxalica/rust-overlay";
    flake-utils.url  = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, rust-overlay, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        overlays = [ (import rust-overlay) ];
        pkgs = import nixpkgs {
          inherit system overlays;
        };
      in
      with pkgs;
      {
        packages.ldbcollector-rust = let
            cargo_nix = import ./rust/Cargo.nix { inherit pkgs nixpkgs; };
          in cargo_nix.rootCrate.build;
        packages.ldbcollector-haskell = pkgs.callPackage ./haskell/default.nix {};
        devShells.default = mkShell {
          packages = with pkgs; [ 
            crate2nix
            cargo-generate
            cargo-wasi
            wasm-bindgen-cli
            wasm
            wasm-pack
            wasmer

            plantumlLicenseName ( graphviz zlib
          ];
          buildInputs = [
            openssl
            pkg-config
            rust-bin.beta.latest.default
            nodejs
          ];

          shellHook = ''
            export RUST_LOG=debug
          '';
        };
      }
    );
}
