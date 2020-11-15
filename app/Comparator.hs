module Comparator where

import qualified Prelude as P
import           MyPrelude

import           Control.Monad
import qualified Data.Vector as V
import           GHC.IO.Encoding
import           System.Environment
import qualified Data.Map as M
import qualified Data.HashMap.Strict as HM
import qualified Data.List as L
import           Data.Aeson.Encode.Pretty (encodePretty)
import           Data.ByteString.Lazy.Char8 (unpack)

import Lib
import Configuration (configuration)

writeCopyleftTable :: FilePath -> [(LicenseName, License)] -> IO ()
writeCopyleftTable outputFolder licenses = let

    computeRow :: License -> Map LicenseFactClassifier CopyleftKind
    computeRow = unpackSLSR . getImpliedCopyleft

    isInconsistent :: (a, Map LicenseFactClassifier CopyleftKind) -> Bool
    isInconsistent (_, m) = ((1 <) . length . L.nub . M.elems) m

    rows :: [(LicenseName, Map LicenseFactClassifier CopyleftKind)]
    rows = filter isInconsistent $ map (\(ln, lic) -> (ln, computeRow lic)) licenses

    writeRow :: (LicenseName, Map LicenseFactClassifier CopyleftKind) -> IO ()
    writeRow (ln, m) = let
        json = (unpack . encodePretty . HM.fromList . M.toList) m
      in do
      print ln
      putStrLn json
      print m

  in mapM_ writeRow rows
