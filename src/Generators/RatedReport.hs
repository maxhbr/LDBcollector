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

import           Model.License
import           Generators.Rating

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

mkRatedReportEntry :: (LicenseName, License) -> (LicenseName, RatedReportEntry)
mkRatedReportEntry (ln,l) = let
    r = applyRatingRules ratingRules (getStatementsFromLicense l)
    spdxId = ln
    otherLicenseNames = []
    licenseText = Nothing
  in (ln, RatedReportEntry r (Just spdxId) ln otherLicenseNames licenseText [] [])

mkRatedReport :: [(LicenseName, License)] -> [(LicenseName, RatedReportEntry)]
mkRatedReport = map mkRatedReportEntry

writeRatedReport :: FilePath -> [(LicenseName, License)] -> IO ()
writeRatedReport targetDir lics = do
  let outputFolder = (targetDir </> "ratedReport")
      rr = mkRatedReport lics
  createDirectory outputFolder
  jsons <- mapM (\(i,rre) -> let
                    outputFile = i ++ ".json"
                in do
                   BL.writeFile (outputFolder </> outputFile) (encode rre)
                   return outputFile) rr
  BL.writeFile (outputFolder </> "_index.json") (encode jsons)


