{-# LANGUAGE OverloadedStrings #-}
module Generators.DetailsWriter
    ( writeDetails
    ) where

import qualified Prelude as P
import           MyPrelude

import qualified Data.Map as M
import           Data.List (stripPrefix)
import qualified Data.Text as T
import qualified Data.Text.IO as T
import           Data.Aeson.Encode.Pretty (encodePretty)
import           Data.ByteString.Lazy.Char8 (unpack)
import qualified Data.Aeson.Lens as AL
import           Data.Char (toLower)
import qualified Text.Pandoc as P
import qualified Text.Pandoc.Builder as P
import           Control.Monad
import           Data.Csv as C
import qualified Data.Vector as V
import qualified Data.ByteString.Lazy as BL

import           Model.License
import           Model.Query
import           Processors.ToPage


writeListOfDetailsToFile :: FilePath -> [LicenseDetails] -> IO ()
writeListOfDetailsToFile csv detailss = let
    bs = C.encodeByName (V.fromList ["Fullname","Shortname","Rating","Copyleft","HasPatentHint", "IsNonCommercial"]) detailss
  in BL.writeFile csv bs

writeDetails :: FilePath -> [Page] -> IO ()
writeDetails outDirectory pages = writeListOfDetailsToFile (outDirectory </> "index.csv") (map pLicenseDetails pages)
