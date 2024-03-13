{
  description = "ldbcollector";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs";
    # src = {
    #   url = "file:.?submodules=1";
    #   type = "git";
    #   flake = false;  # not including this results in inifite recursion
    # };
  };

  outputs = inputs@{ self, nixpkgs, ... }:let
    system = "x86_64-linux";

    pkgs = nixpkgs.legacyPackages.${system};
    lib = pkgs.lib;

    t = lib.trivial;
    hl = pkgs.haskell.lib;

    extraLibraries = with pkgs; [
        plantuml
        graphviz
        zlib
        libffi
    ];
    project = devTools:
      let addBuildTools = (t.flip hl.addBuildTools) devTools;
          addExtraLibraries = (t.flip hl.addExtraLibraries) extraLibraries;
      in pkgs.haskellPackages.developPackage {
        root = ./.;
        name = "ldbcollector";
        returnShellEnv = !(devTools == [ ]);

        modifier = (t.flip t.pipe) [
          addBuildTools
          addExtraLibraries
          hl.dontHaddock
          # hl.dontCheck # checks fail, as the ./data folder with its submodules is not set up correctly in nix
          hl.enableStaticLibraries
          hl.justStaticExecutables
          hl.disableLibraryProfiling
          hl.disableExecutableProfiling
          ((t.flip hl.appendBuildFlags) ["--ghc-options=\" -threaded -rtsopts -with-rtsopts=-N\"" "+RTS"])
        ];
      };

  in {
    packages.${system} = rec {
      # data = "${inputs.src}/data";
      ldbcollector = project [];
      ldbcollector-untested = hl.dontCheck self.packages.${system}.ldbcollector;
      default = ldbcollector;
    };
    apps.${system} = rec {
      ldbcollector = {
        type = "app";
        program = "${self.packages.${system}.ldbcollector-untested}/bin/ldbcollector-exe";
      };
      default = ldbcollector;
    };

    devShell.${system} = project (with pkgs.haskellPackages; [
      cabal-fmt
      cabal-install
      haskell-language-server
      hlint
      ghcid
    ]);
  };
}
