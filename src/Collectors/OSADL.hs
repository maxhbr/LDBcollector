{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE OverloadedStrings #-}
module Collectors.OSADL
  ( loadOsadlFacts
  ) where

import Prelude hiding (id)

import           System.FilePath
import           System.Directory
import           Data.List
import qualified Data.Text as T
import qualified Data.Vector as V
import           Debug.Trace (trace)
import qualified Data.ByteString as B
import           Data.ByteString (ByteString)
import qualified Data.ByteString.Char8 as Char8

import           Data.Aeson
import           GHC.Generics

import           Model.License

data OSADLFactRaw
  = OSADLFactRaw
  { spdxId :: LicenseShortname
  , osadlRule :: ByteString
  } deriving (Show, Generic)
instance ToJSON ByteString where
  toJSON = toJSON . Char8.unpack
instance ToJSON OSADLFactRaw
instance LFRaw OSADLFactRaw where
  getImpliedShortnames (OSADLFactRaw sn _) = [sn]
  getType _                                = "OSADLFact"


loadOsadlFactFromFile :: FilePath -> FilePath -> IO LicenseFact
loadOsadlFactFromFile osadlFolder osadlFile = let
    fileWithPath = osadlFolder </> osadlFile
    spdxId = dropExtension osadlFile
  in do
    content <- B.readFile fileWithPath
    return (mkLicenseFact "OSADL" (OSADLFactRaw spdxId content))

loadOsadlFacts :: FilePath -> IO Facts
loadOsadlFacts osadlFolder = do
  files <- getDirectoryContents osadlFolder
  let osadls = filter ("osadl" `isSuffixOf`) files
  facts <- mapM (loadOsadlFactFromFile osadlFolder) osadls
  return (V.fromList facts)
