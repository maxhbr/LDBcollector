
{-# LANGUAGE OverloadedStrings #-}
module Ldbcollector.Source.OSADL
  ( OSADL (..)
  ) where

import           Ldbcollector.Model    hiding (ByteString)

import qualified Data.Vector as V
import qualified Data.ByteString as B
import           Data.ByteString (ByteString)
import qualified Data.ByteString.Char8 as Char8

data OSADLFactRaw
  = OSADLFactRaw
  { spdxId :: LicenseName
  , osadlRule :: ByteString
  } deriving (Show, Generic)

getTaskFromOSADL :: FilePath -> IO LicenseGraphTask
getTaskFromOSADL osadl = do
    putStrLn ("read " ++ osadl)
    let id = takeBaseName osadl
    contents <- readFile osadl
    let contentLines = lines contents
    return $
        EdgeLeft (AddTs. V.fromList $ [
            "Copyleft" `ifToTask` ("COPYLEFT CLAUSE Questionable" `elem` contentLines)
        ]) (Potentially AppliesTo) $
        EdgeLeft (AddTs. V.fromList $ [
            "Patent hint" `ifToTask` ("PATENT HINTS Yes" `elem` contentLines),
            "Copyleft" `ifToTask` ("COPYLEFT CLAUSE Yes" `elem` contentLines)
        ]) AppliesTo $
        Edge ((Add . Rule . pack) contents) AppliesTo $
        Edge ((Add . LicenseName . newNLN "osadl" . pack) id) Same $
        Add ((LicenseName . newNLN "spdx" . pack) id)

newtype OSADL = OSADL FilePath
instance Source OSADL where
    getTask (OSADL dir) = do
        osadls <- glob (dir </> "*.osadl")
        AddTs . V.fromList <$> mapM getTaskFromOSADL osadls





-- osadlLFC :: LicenseFactClassifier
-- osadlLFC = LFCWithLicense (LFL "NOASSERTION") "OSADL License Checklist"
-- instance LicenseFactClassifiable OSADLFactRaw where
--   getLicenseFactClassifier _ = osadlLFC
-- instance LFRaw OSADLFactRaw where
--   getImpliedNames (OSADLFactRaw sn _)                                                      = CLSR [sn]
--   getImpliedCopyleft f@(OSADLFactRaw _ r) | "COPYLEFT CLAUSE Questionable" `B.isInfixOf` r = mkSLSR f MaybeCopyleft
--                                           | "COPYLEFT CLAUSE Yes"          `B.isInfixOf` r = mkSLSR f Copyleft
--                                           | otherwise                                      = NoSLSR
--   getHasPatentnHint f@(OSADLFactRaw _ r)  | "PATENT HINTS Yes"             `B.isInfixOf` r = mkRLSR f 90 True
--                                           | otherwise                                      = NoRLSR


-- loadOsadlFactFromEntry :: (FilePath, ByteString) ->  LicenseFact
-- loadOsadlFactFromEntry (osadlFile,content) = let
--     spdxId = dropExtension osadlFile
--   in LicenseFact (Just $ "https://www.osadl.org/fileadmin/checklists/unreflicenses/" ++ spdxId ++ ".txt") (OSADLFactRaw spdxId content)

-- osadlFolder :: [(FilePath, ByteString)]
-- osadlFolder = $(embedDir "data/OSADL/")

-- loadOsadlFacts :: IO Facts
-- loadOsadlFacts = let
--     facts = map loadOsadlFactFromEntry (filter (\(fp,_) -> "osadl" `isSuffixOf` fp) osadlFolder)
--   in do
--     logThatFactsAreLoadedFrom "OSADL License Checklist"
--     logThatOneHasFoundFacts "OSADL License Checklist" facts
--     return (V.fromList facts)
