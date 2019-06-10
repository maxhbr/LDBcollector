{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE OverloadedStrings #-}
module Generators.RatedReport
    ( mkRatedReport
    , writeRatedReport
    ) where

import qualified Prelude as P
import           MyPrelude

import qualified Data.Text as T
import qualified Data.Vector as V
import qualified Data.ByteString.Lazy as BL
import           Control.Monad
import           Control.Monad.Trans.Writer.Strict (execWriter, tell)
import qualified Data.Map as M

import           Model.License
import           Generators.Rating

data RatedReportConfiguration
  = RatedReportConfiguration
  { selectedLicenses :: [LicenseName]
  , ratingOverwrites :: Map LicenseName Rating
  }

ratingRules :: [RatingRule]
ratingRules = let
    addRule desc fun = tell . (:[]) $ RatingRule desc fun
    getStatementsWithLabel label = V.filter (\stmt -> extractLicenseStatementLabel stmt == label)
    getStatementsWithLabelFromSource label source = V.filter (\stmt -> (extractLicenseStatementLabel stmt == label)
                                                                        && (_factSourceClassifier stmt == source))
  in execWriter $ do
    addRule "should have at least one positive rating to be Go" $ let
        fn = (== 0) . V.length . getStatementsWithLabel possitiveRatingLabel
      in ruleFunctionFromCondition fn (removeRatingFromState RGo)
    addRule "should have no negative ratings to be Go" $ let
        fn = (> 0) . V.length . getStatementsWithLabel negativeRatingLabel
      in ruleFunctionFromCondition fn (removeRatingFromState RGo)
    addRule "Fedora bad Rating implies at least Stop" $ let
        fn = (> 0) . V.length . getStatementsWithLabelFromSource negativeRatingLabel (LFC ["FedoraProjectWiki", "FPWFact"])
      in ruleFunctionFromCondition fn (removeRatingFromState RGo . removeRatingFromState RAtention)
    addRule "Blue Oak Lead Rating implies at least Stop" $ let
        fn = (> 0) . V.length . getStatementsWithLabelFromSource negativeRatingLabel (LFC ["BlueOak", "BOEntry"])
      in ruleFunctionFromCondition fn (removeRatingFromState RGo . removeRatingFromState RAtention)

data RatedReportEntry
  = RatedReportEntry
  { rrRating :: Rating
  , rrSpdxId :: Maybe LicenseName
  , rrLicenseName :: LicenseName
  , rrOtherLicenseNames :: [LicenseName]
  , rrLicenseText :: Maybe Text
  , rrLinks :: [(Text, Text)]
  , rrOtherLinks :: [Text]
  } deriving (Show, Generic)
instance ToJSON RatedReportEntry

mkRatedReportEntry :: RatedReportConfiguration -> (LicenseName, License) -> (LicenseName, RatedReportEntry)
mkRatedReportEntry (RatedReportConfiguration _ rOs) (ln,l) = let
    r = let
        calculatedR = applyRatingRules ratingRules (getStatementsFromLicense l)
      in M.findWithDefault calculatedR ln rOs
    spdxId = ln
    otherLicenseNames = []
    licenseText = Nothing
  in (ln, RatedReportEntry r (Just spdxId) ln otherLicenseNames licenseText [] [])

mkRatedReport ::  RatedReportConfiguration -> [(LicenseName, License)] -> [(LicenseName, RatedReportEntry)]
mkRatedReport conf@(RatedReportConfiguration sLSNs _) lics = let
    selectedLics = filter (\(sn, _) -> sn `elem` sLSNs) lics
  in map (mkRatedReportEntry conf) selectedLics

writeRatedReport :: RatedReportConfiguration -> FilePath -> [(LicenseName, License)] -> IO ()
writeRatedReport conf targetDir lics = do
  let outputFolder = targetDir </> "ratedReport"
      rr = mkRatedReport conf lics
  createDirectory outputFolder
  jsons <- mapM (\(i,rre) -> let
                    outputFile = i ++ ".json"
                in do
                   BL.writeFile (outputFolder </> outputFile) (encode rre)
                   return outputFile) rr
  BL.writeFile (outputFolder </> "_index.json") (encode jsons)


