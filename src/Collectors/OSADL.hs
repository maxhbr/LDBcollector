{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE TemplateHaskell #-}
module Collectors.OSADL
  ( loadOsadlFacts
  ) where

import qualified Prelude as P
import           MyPrelude hiding (id, ByteString)
import           Collectors.Common

import qualified Data.Text as T
import qualified Data.Vector as V
import qualified Data.ByteString as B
import           Data.ByteString (ByteString)
import qualified Data.ByteString.Char8 as Char8
import           Data.FileEmbed (embedDir)

import           Model.License

data OSADLFactRaw
  = OSADLFactRaw
  { spdxId :: LicenseName
  , osadlRule :: ByteString
  } deriving (Show, Generic)
instance ToJSON ByteString where
  toJSON = toJSON . Char8.unpack
instance ToJSON OSADLFactRaw
osadlLFC :: LicenseFactClassifier
osadlLFC = LFC "OSADL License Checklist"
instance LFRaw OSADLFactRaw where
  getLicenseFactClassifier _                                                               = osadlLFC
  getImpliedNames (OSADLFactRaw sn _)                                                      = CLSR [sn]
  getImpliedCopyleft f@(OSADLFactRaw _ r) | "COPYLEFT CLAUSE Questionable" `B.isInfixOf` r = mkSLSR f MaybeCopyleft
                                          | "COPYLEFT CLAUSE Yes"          `B.isInfixOf` r = mkSLSR f Copyleft
                                          | otherwise                                      = NoSLSR
  getHasPatentnHint f@(OSADLFactRaw _ r) | "PATENT HINTS Yes" `B.isInfixOf` r              = mkRLSR f 90 True
                                         | otherwise                                       = NoRLSR


loadOsadlFactFromEntry :: (FilePath, ByteString) ->  LicenseFact
loadOsadlFactFromEntry (osadlFile,content) = let
    spdxId = dropExtension osadlFile
  in LicenseFact (Just $ "https://www.osadl.org/fileadmin/checklists/unreflicenses/" ++ spdxId ++ ".txt") (OSADLFactRaw spdxId content)

osadlFolder :: [(FilePath, ByteString)]
osadlFolder = $(embedDir "data/OSADL/")

loadOsadlFacts :: IO Facts
loadOsadlFacts = let
    facts = map loadOsadlFactFromEntry (filter (\(fp,_) -> "osadl" `isSuffixOf` fp) osadlFolder)
  in do
    logThatFactsAreLoadedFrom "OSADL License Checklist"
    return (V.fromList facts)
