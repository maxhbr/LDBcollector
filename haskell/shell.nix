{ nixpkgs ? import <nixpkgs> {}, compiler ? "default", doBenchmark ? false }:

let

  inherit (nixpkgs) pkgs;

  f = { mkDerivation, aeson, aeson-pretty, base, bytestring
      , cassava, containers, directory, fgl, file-embed, filepath, Glob
      , graphviz, hspec, lib, mtl, QuickCheck, spdx, temporary, text
      , unordered-containers, vector, yaml
      }:
      mkDerivation {
        pname = "ldbcollector";
        version = "2.0.0.0";
        src = ./.;
        isLibrary = true;
        isExecutable = true;
        libraryHaskellDepends = [
          aeson aeson-pretty base bytestring cassava containers directory fgl
          filepath Glob graphviz mtl spdx text unordered-containers vector
          yaml
        ];
        executableHaskellDepends = [ base ];
        testHaskellDepends = [
          base containers fgl file-embed hspec QuickCheck temporary
          unordered-containers vector
        ];
        homepage = "https://github.com/maxhbr/LDBcollector/";
        license = lib.licenses.bsd3;
        mainProgram = "ldbcollector";
      };

  haskellPackages = if compiler == "default"
                       then pkgs.haskellPackages
                       else pkgs.haskell.packages.${compiler};

  variant = if doBenchmark then pkgs.haskell.lib.doBenchmark else pkgs.lib.id;

  drv = variant (haskellPackages.callPackage f {});

in

  if pkgs.lib.inNixShell then drv.env else drv
