{
  description = "ldbcollector";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs";
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
      ldbcollector = project [];
      ldbcollector-untested = hl.dontCheck self.packages.${system}.ldbcollector;
      ldbcollector-image = pkgs.dockerTools.buildImage {
        name = "maxhbr/ldbcollector";
        tag = "latest";

        config = {
            Cmd = [ "${self.packages.${system}.ldbcollector-untested}/bin/ldbcollector-exe" ];
            WorkingDir = "/ldbcollector";
            Env = [
                "LC_ALL=en_US.UTF-8"
                "LANG=en_US.UTF-8"
                "LANGUAGE=en_US.UTF-8"
            ];
            Volumes = {
                "/ldbcollector/data" = {};
            };
        };

        created = "now";
      };
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
