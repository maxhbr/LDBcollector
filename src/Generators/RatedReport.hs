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
    telli = tell . (:[])
    countNumberOfStatementsWithLabel label stmts = V.length (V.filter (\stmt -> extractLicenseStatementLabel stmt == label) stmts)
    countNumberOfStatementsWithLabelFromSource label source stmts = V.length (V.filter (\stmt -> (extractLicenseStatementLabel stmt == label)
                                                                                              && (_factSourceClassifier stmt == source)) stmts)
  in execWriter $ do
    telli $ let
        fn = countNumberOfStatementsWithLabel "possitiveRating"
      in RatingRule "should have at least one positive rating to be Go"
                    (ruleFunctionFromCondition (\stmts -> fn stmts == 0)
                                               (removeRatingFromState RGo))
    telli $ let
        fn = countNumberOfStatementsWithLabel "negativeRating"
      in RatingRule "should have no negative ratings to be Go"
                    (ruleFunctionFromCondition (\stmts -> fn stmts > 0)
                                               (removeRatingFromState RGo))
    telli $ let
        fn = countNumberOfStatementsWithLabelFromSource "negativeFedoraRating" (LFC ["FedoraProjectWiki", "FPWFact"])
      in RatingRule "Fedora bad Rating implies at least Stop"
                    (ruleFunctionFromCondition (\stmts -> fn stmts > 0)
                                               (removeRatingFromState RGo . removeRatingFromState RAtention))
    telli $ let
        fn = countNumberOfStatementsWithLabelFromSource "negativeFedoraRating" (LFC ["BlueOak", "BOEntry"])
      in RatingRule "Fedora bad Rating implies at least Stop"
                    (ruleFunctionFromCondition (\stmts -> fn stmts > 0)
                                               (removeRatingFromState RGo . removeRatingFromState RAtention))

data RatedReportEntry
  = RatedReportEntry
  { rrRating :: Rating
  , rrSpdxId
  , rrLicenseName :: LicenseName
  , rrOtherLicenseNames :: [LicenseName]
  , rrLicenseText :: Maybe Text
  } deriving (Show, Generic)
instance ToJSON RatedReportEntry

mkRatedReportEntry :: (LicenseName, License) -> (LicenseName, RatedReportEntry)
mkRatedReportEntry (ln,l) = let
    r = applyRatingRules ratingRules (getStatementsFromLicense l)
    spdxId = ln
    otherLicenseNames = []
    licenseText = Nothing
  in (ln, RatedReportEntry r spdxId ln otherLicenseNames licenseText)

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


