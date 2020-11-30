module Generators.FactJsonsWriter
  ( writeFactJSONs
  ) where


import qualified Prelude as P
import           MyPrelude

import qualified Data.Vector as V
import qualified Data.Map as M
import qualified Data.ByteString.Lazy as BL
import           Data.Aeson.Encode.Pretty (encodePretty)
import           GHC.IO.Encoding (setLocaleEncoding, utf8)
import           System.Environment
import qualified Data.ByteString as B
import qualified Crypto.Hash.MD5 as MD5
import qualified Data.ByteString.Base16 as B16
import qualified Data.ByteString.Char8 as Char8

import           Model.License

computeMD5 :: BL.ByteString -> String
computeMD5 bs = let
  hash = MD5.hashlazy bs
  hash16 = B16.encode hash
  hashStr = Char8.unpack hash16
  in hashStr

writeFactJSONs :: FilePath -> Facts -> IO ()
writeFactJSONs outputFolder facts = do
  let jsonOutputFolder = outputFolder </> "_raw_facts"
  createDirectory jsonOutputFolder
  mapM_ (\f -> let
            pBS = encodePretty f
            pOutputFile = (computeMD5 pBS) ++ ".pretty.json"
            in BL.writeFile (jsonOutputFolder </> pOutputFile) (pBS)) facts
