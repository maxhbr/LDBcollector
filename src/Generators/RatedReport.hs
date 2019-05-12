{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE OverloadedStrings #-}
module Generators.RatedReport
    ( mkRatedReport
    ) where

import qualified Prelude as P
import           MyPrelude

import qualified Data.Text as T
import qualified Data.Vector as V

import           Model.License

data RatedReportRating
  = RRR_Go -- can be used
  | RRR_Atention -- needs more atention
  | RRR_Stop -- needs aproval
  | RRR_NoGo -- can't be used
  | RRR_Unknown [RatedReportRating]
  deriving (Show, Generic, Eq)
instance ToJSON RatedReportRating

-- to keep track of current possibilities
data RatedReportRatingState
  = RatedReportRatingState
  { rrrsGo :: Bool
  , rrrsAtention :: Bool
  , rrrsStop :: Bool
  , rrrsNoGo :: Bool
  }
type RatedReportRatingStateMutator
  = RatedReportRatingState -> RatedReportRatingState
initialReportRatingState :: RatedReportRatingState
initialReportRatingState = RatedReportRatingState True True True True
removeRatingFromState :: RatedReportRating -> RatedReportRatingStateMutator
removeRatingFromState RRR_Go rrrs = rrrs{rrrsGo = False}
removeRatingFromState RRR_Atention rrrs = rrrs{rrrsAtention = False}
removeRatingFromState RRR_Stop rrrs = rrrs{rrrsStop = False}
removeRatingFromState RRR_NoGo rrrs = rrrs{rrrsNoGo = False}
removeRatingFromState _        rrrs = rrrs -- TODO??
setRatingOfState :: RatedReportRating -> RatedReportRatingStateMutator
setRatingOfState RRR_Go = removeRatingFromState RRR_Atention . removeRatingFromState RRR_Stop . removeRatingFromState RRR_NoGo
setRatingOfState RRR_Atention = removeRatingFromState RRR_Go . removeRatingFromState RRR_Stop . removeRatingFromState RRR_NoGo
setRatingOfState RRR_Stop = removeRatingFromState RRR_Go . removeRatingFromState RRR_Atention . removeRatingFromState RRR_NoGo
setRatingOfState RRR_NoGo = removeRatingFromState RRR_Go . removeRatingFromState RRR_Atention . removeRatingFromState RRR_Stop
setRatingOfState _ = removeRatingFromState RRR_Go . removeRatingFromState RRR_Atention . removeRatingFromState RRR_Stop . removeRatingFromState RRR_NoGo -- TODO??
ratingFromRatedReportRatingState :: RatedReportRatingState -> RatedReportRating
ratingFromRatedReportRatingState rrrs = let
    mapFromState :: (RatedReportRatingState -> Bool) -> RatedReportRating -> RatedReportRatingState -> Maybe RatedReportRating
    mapFromState getter result state = if getter state
                                       then Just result
                                       else Nothing
    ratingFromSetOfRatings :: [RatedReportRating] -> RatedReportRating
    ratingFromSetOfRatings [r] = r
    ratingFromSetOfRatings rs = RRR_Unknown rs
  in ratingFromSetOfRatings . catMaybes $ map (\f -> f rrrs) [ mapFromState rrrsGo RRR_Go
                                                             , mapFromState rrrsAtention RRR_Atention
                                                             , mapFromState rrrsStop RRR_Stop
                                                             , mapFromState rrrsNoGo RRR_NoGo
                                                             ]

type RatedReportRatingRuleFun
  = Statements -> RatedReportRatingStateMutator
data RatedReportRatingRule
  = RatedReportRatingRule
  { rrrrDescription :: Text
  , rrrrFunction :: RatedReportRatingRuleFun
  }
instance Show RatedReportRatingRule where
  show (RatedReportRatingRule desc _) = T.unpack desc

ruleFunctionFromCondition :: (Statements -> Bool) -> RatedReportRatingStateMutator -> RatedReportRatingRuleFun
ruleFunctionFromCondition condition fun l = if condition l
                                            then fun
                                            else id
negativeRuleFunctionFromCondition :: (Statements -> Bool) -> RatedReportRatingStateMutator -> RatedReportRatingRuleFun
negativeRuleFunctionFromCondition condition = ruleFunctionFromCondition (not . condition)

applyRatingRules :: [RatedReportRatingRule] -> Statements -> RatedReportRating
applyRatingRules rrrrs stmts = let
    applyRatingRules' :: [RatedReportRatingRule] -> RatedReportRatingState
    applyRatingRules' = foldr (`rrrrFunction` stmts) initialReportRatingState
  in ratingFromRatedReportRatingState (applyRatingRules' rrrrs)

ratingRules :: [RatedReportRatingRule]
ratingRules = let
    countNumberOfStatementsWithLabel label stmts = V.length (V.filter (\stmt -> extractLicenseStatementLabel stmt == label) stmts)
    rr1 = let
        countNumberOfPositiveRatings = countNumberOfStatementsWithLabel "possitiveRating"
      in RatedReportRatingRule "should have at least one positive rating to be Go"
                               (ruleFunctionFromCondition (\stmts -> countNumberOfPositiveRatings stmts == 0) (removeRatingFromState RRR_Go))
    rr2 = let
        countNumberOfNegativeRatings = countNumberOfStatementsWithLabel "negativeRating"
      in RatedReportRatingRule "should have no negative ratings to be Go"
                               (ruleFunctionFromCondition (\stmts -> countNumberOfNegativeRatings stmts > 0) (removeRatingFromState RRR_Go))
  in [ rr1, rr2 ]

data RatedReportEntry
  = RatedReportEntry
  { rrRating :: RatedReportRating
  , rrSpdxId
  , rrLicenseName :: LicenseName
  , rrOtherLicenseNames :: [LicenseName]
  , rrLicenseText :: Maybe Text
  } deriving (Show, Generic)
instance ToJSON RatedReportEntry

mkRatedReportEntry :: (LicenseName, License) -> RatedReportEntry
mkRatedReportEntry (ln,l) = let
    rrr = applyRatingRules ratingRules (getStatementsFromLicense l)
    spdxId = ln
    otherLicenseNames = []
    licenseText = Nothing
  in RatedReportEntry rrr spdxId ln otherLicenseNames licenseText

mkRatedReport :: [(LicenseName, License)] -> [RatedReportEntry]
mkRatedReport = map mkRatedReportEntry

