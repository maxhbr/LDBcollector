module Generators.LicenseJsonsWriter
  ( writeLicenseJSONs
  ) where

import qualified Prelude as P
import           MyPrelude

import qualified Data.Vector as V
import qualified Data.Map as M
import qualified Data.ByteString.Lazy as BL
import           Data.Aeson.Encode.Pretty (encodePretty)
import           GHC.IO.Encoding (setLocaleEncoding, utf8)
import           System.Environment

import           Model.License

writeLicenseJSONs :: FilePath -> [(LicenseName, License)] -> IO ()
writeLicenseJSONs outputFolder licenses = do
  let jsonOutputFolder = outputFolder </> "json"
  createDirectory jsonOutputFolder
  jsons <- mapM (\(i,l) -> let
                    outputFile = i ++ ".json"
                    pOutputFile = i ++ ".pretty.json"
                in do
                   BL.writeFile (jsonOutputFolder </> outputFile) (encode l)
                   BL.writeFile (jsonOutputFolder </> pOutputFile) (encodePretty l)
                   return outputFile) licenses
  BL.writeFile (jsonOutputFolder </> "_all.json") (encodePretty licenses)
  BL.writeFile (jsonOutputFolder </> "_index.json") (encodePretty jsons)
