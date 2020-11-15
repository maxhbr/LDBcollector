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
import qualified Data.Text as T
import           Data.Aeson.Encode.Pretty (encodePretty)
import qualified Data.Aeson as A
import           Data.ByteString.Lazy.Char8 (unpack)
import qualified Data.ByteString.Lazy as BL
import           Data.List.Extra (groupSort)

import Lib
import Configuration (configuration)

writeCopyleftTable :: FilePath -> [(LicenseName, License)] -> IO ()
writeCopyleftTable outDirectory licenses = let

    computeRow :: License -> Map LicenseFactClassifier CopyleftKind
    computeRow = unpackSLSR . getImpliedCopyleft

    isInconsistent :: (a, Map LicenseFactClassifier CopyleftKind) -> Bool
    isInconsistent (_, m) = ((1 <) . length . L.nub . M.elems) m

    rows :: [(LicenseName, Map LicenseFactClassifier CopyleftKind)]
    rows = filter isInconsistent $ map (\(ln, lic) -> (ln, computeRow lic)) licenses

    writeRow
      :: FilePath
      -> (LicenseName, Map LicenseFactClassifier CopyleftKind)
      -> IO (Text, HM.HashMap Text (Vector Text))
    writeRow cOutDirectory (ln, m) = let
        mapToObject =
          HM.fromList .
          (map (\(ck,lfcs) -> (ck, V.fromList lfcs))) .
          groupSort .
          (map (\(lfc,ck) -> (T.pack $ show ck, T.pack $ show lfc))) .
          M.toList
        jsonObject = mapToObject m
        jsonString = encodePretty jsonObject
      in do
        BL.writeFile (cOutDirectory </> (ln ++ ".json")) jsonString
        return (T.pack ln, jsonObject)

  in do
    -- createDirectoryIfNotExists (outDirectory </> "_stats")
    let cOutDirectory = outDirectory </> "_stats" </> "copyleft"
    createDirectoryIfNotExists cOutDirectory

    tuples <- mapM (writeRow cOutDirectory) rows
    let allString = (encodePretty . HM.fromList) tuples
    BL.writeFile (cOutDirectory </> ("_all.json")) allString
