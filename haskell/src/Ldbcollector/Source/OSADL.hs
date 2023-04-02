
{-# LANGUAGE OverloadedStrings #-}
module Ldbcollector.Source.OSADL
  ( OSADL (..)
  ) where

import           Ldbcollector.Model    hiding (ByteString)

import qualified Data.Vector as V
import           Data.ByteString (ByteString)
import qualified Data.Text as T
import qualified Data.Text.IO as T

data OSADLFact
  = OSADLFact
  { spdxId :: LicenseName
  , osadlRule :: Text
  } deriving (Show, Eq, Ord, Generic)
instance ToJSON OSADLFact

instance LicenseFactC OSADLFact where
    getType _ = "OSADL"
    getApplicableLNs (OSADLFact id _) = NLN id `AlternativeLNs` [LN (setNS "spdx" id)]
    getImpliedStmts (OSADLFact _ rule) = let
            ruleLines = T.lines rule
        in [ LicenseRule rule `SubStatements` [ "Copyleft" `ifToStmt` ("COPYLEFT CLAUSE Yes" `elem` ruleLines)
                                              , "Patent hint" `ifToStmt` ("PATENT HINTS Yes" `elem` ruleLines)
                                              , "maybe Copyleft" `ifToStmt` ("COPYLEFT CLAUSE Questionable" `elem` ruleLines)
                                              ]
           ]

getOSADL :: FilePath -> IO OSADLFact
getOSADL osadl = do
    putStrLn ("read " ++ osadl)
    let id = takeBaseName osadl
    contents <- T.readFile osadl
    return (OSADLFact ((newNLN "osadl" . pack) id) contents)

newtype OSADL = OSADL FilePath
instance Source OSADL where
    getOrigin _ = Origin "OSADL"
    getFacts (OSADL dir) = do
        osadls <- glob (dir </> "*.osadl")
        V.fromList . map wrapFact <$> mapM getOSADL osadls