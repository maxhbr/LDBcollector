module Generators.FactLicenses
  ( writeFactsLicenses
  ) where

import qualified Prelude as P
import           MyPrelude

import qualified Data.Vector as V
import qualified Data.Map as M
import qualified Data.Text.IO as T

import           Model.License
import           Generators.FindClusters

writeFactsLicenses :: FilePath -> Facts -> [(LicenseName, (License, a))] -> IO ()
writeFactsLicenses outputFolder facts licenses = let
    lfls :: [(Text, LicenseFactLicense)]
    lfls = (V.toList . V.uniq . V.map (\lfc -> (extractBrc lfc, extractLFL lfc)) . V.map getLicenseFactClassifier) facts
    licenseMap = (M.fromList . map (\(ln, (l, _)) -> (ln, l))) licenses
  in mapM_ (\tpl@(_, lfl) ->
              let
                licensename = extractLFLName lfl
                outfile = outputFolder </> "LICENSE." ++ licensename
              in do
                print tpl
                when (licensename /= "") $
                  case licensename `M.lookup` licenseMap of
                    Just lic -> case unpackRLSR (getImpliedText lic) of
                      Just text -> T.writeFile outfile text
                      _         -> hPutStrLn stderr ("... found no text for: " ++ licensename)
                    _         -> hPutStrLn stderr ("... found no license for: " ++ licensename)
           ) lfls
