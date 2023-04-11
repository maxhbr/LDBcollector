
{-# LANGUAGE OverloadedStrings #-}
module Ldbcollector.Source.OSADL
  ( OSADL (..)
  ) where

import           Ldbcollector.Model

import qualified Data.Vector as V
import qualified Data.Text as T
import qualified Data.Text.IO as T
import qualified Text.Blaze.Html5                   as H

data OSADLRule
  = OSADLRule
  { spdxId :: LicenseName
  , osadlRule :: Text
  } deriving (Show, Eq, Ord, Generic)
instance ToJSON OSADLRule

instance LicenseFactC OSADLRule where
    getType _ = "OSADLRule"
    getApplicableLNs (OSADLRule id _) = LN id `AlternativeLNs` [LN (setNS "spdx" id)]
    getImpliedStmts (OSADLRule _ rule) = let
            ruleLines = T.lines rule
        in [ LicenseRule rule `SubStatements` [ if "COPYLEFT CLAUSE Yes" `elem` ruleLines
                                                then typestmt "Copyleft"
                                                else MaybeStatement Nothing
                                              , "Patent hint" `ifToStmt` ("PATENT HINTS Yes" `elem` ruleLines)
                                              , "maybe Copyleft" `ifToStmt` ("COPYLEFT CLAUSE Questionable" `elem` ruleLines)
                                              ]
           ]
    toMarkup (OSADLRule _ rule) = H.pre (H.toMarkup rule)

getOSADL :: FilePath -> IO OSADLRule
getOSADL osadl = do
    logFileReadIO osadl
    let id = takeBaseName osadl
    contents <- T.readFile osadl
    return (OSADLRule ((newNLN "osadl" . pack) id) contents)

data OSADLMatrixCompatibility
    = OSADLMatrixCompatibility
    { _other :: LicenseName
    , _compatibility :: String
    , _explanation :: Text
    } deriving (Show, Eq, Ord, Generic)
instance FromJSON OSADLMatrixCompatibility where
  parseJSON = withObject "OSADLMatrixCompatibility" $ \v ->
    OSADLMatrixCompatibility <$> v .: "name"
                             <*> v .: "compatibility"
                             <*> v .: "explanation"
instance ToJSON OSADLMatrixCompatibility

data OSADLMatrixLicense
    = OSADLMatrixLicense
    { _name :: LicenseName
    , compatibilities :: [OSADLMatrixCompatibility]
    } deriving (Show, Eq, Ord, Generic)
instance ToJSON OSADLMatrixLicense
instance FromJSON OSADLMatrixLicense where
  parseJSON = withObject "OSADLMatrixLicense" $ \v ->
    OSADLMatrixLicense <$> (setNS "osadl" <$> v .: "name")
                       <*> v .: "compatibilities"
instance LicenseFactC OSADLMatrixLicense where
    getType _ = "OSADLMatrix"
    getApplicableLNs (OSADLMatrixLicense name _) = LN name
    getImpliedStmts (OSADLMatrixLicense _ cs) = let
            compatibilities = map (\(OSADLMatrixCompatibility other compatibility explanation) -> LicenseCompatibility other compatibility explanation) cs
        in [LicenseCompatibilities compatibilities]

newtype OSADLMatrix = OSADLMatrix (V.Vector OSADLMatrixLicense)
    deriving (Show, Eq, Ord, Generic)
instance FromJSON OSADLMatrix where
  parseJSON = withObject "OSADLMatrix" $ \v -> OSADLMatrix <$> v .: "licenses"

getOSADLMatrix :: FilePath -> IO OSADLMatrix
getOSADLMatrix json = do
    logFileReadIO json
    decoded <- eitherDecodeFileStrict json :: IO (Either String OSADLMatrix)
    case decoded of
        Left err  -> fail err
        Right m -> return m

newtype OSADL
    = OSADL FilePath
instance Source OSADL where
    getSource _ = Source "OSADL"
    getFacts (OSADL dir) = do
        osadls <- glob (dir </> "unreflicenses" </> "*.txt")
        rules <- V.fromList . map wrapFact <$> mapM getOSADL osadls
        OSADLMatrix fromMatrix <- getOSADLMatrix (dir </> "matrixseqexpl.json")
        return $ rules <> V.map wrapFact fromMatrix