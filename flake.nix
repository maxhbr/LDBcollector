

{
  description = "ramda.guide";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/master";
    naersk = {
      url = "github:nmattia/naersk";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    rust-overlay = {
      url = "github:oxalica/rust-overlay";
      flake = false;
      inputs.nixpkgs.follows = "nixpkgs";
    };
    utils = {
      url = "github:numtide/flake-utils";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { naersk, nixpkgs, rust-overlay, self, utils }:
    utils.lib.eachDefaultSystem (system:
      let
        rust-overlay' = import rust-overlay;
        pkgs = import nixpkgs {
          inherit system;
          overlays = [ rust-overlay' ];
        };
        rust = (pkgs.rustChannelOf {
          date = "2022-10-29";
          channel = "nightly";
        }).rust;
        naersk-lib = naersk.lib."${system}".override {
          cargo = rust;
          rustc = rust;
        };
      in rec {
        packages = utils.lib.flattenTree {
          ldbcolector = naersk-lib.buildPackage {
            pname = "ldbcolector";
            root = ./.;
          };
        };

        defaultPackage = packages.ldbcolector;

        apps.ldbcolector = utils.lib.mkApp {
          drv = packages.ldbcolector;
        };

        defaultApp = apps.ldbcolector;

        devShell = pkgs.mkShell {
          buildInputs = with pkgs;[ 
            rustup
          ];
          nativeBuildInputs = [ rust ];
        };
      }
    );
}
