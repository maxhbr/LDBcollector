
{-# LANGUAGE OverloadedStrings #-}
module Ldbcollector.Source.OSADL
  ( OSADL (..)
  ) where

import           Ldbcollector.Model    hiding (ByteString)

import qualified Data.Vector as V
import           Data.ByteString (ByteString)

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