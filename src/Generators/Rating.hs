{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE OverloadedStrings #-}
module Generators.Rating
    ( Rating (..)
    , removeRatingFromState, setRatingOfState
    , ruleFunctionFromCondition, negativeRuleFunctionFromCondition
    , RatingRule (..), RatingRuleFun
    , applyRatingRules
    ) where

import qualified Prelude as P
import           MyPrelude

import qualified Data.Text as T
import qualified Data.Vector as V
import qualified Data.ByteString.Lazy as BL

import           Model.License

data Rating
  = RGo -- can be used
  | RAtention -- needs more atention
  | RStop -- needs aproval
  | RNoGo -- can't be used
  | RUnknown [Rating]
  deriving (Show, Generic, Eq)
instance ToJSON Rating

-- to keep track of current possibilities
data RatingState
  = RatingState
  { rsGo :: Bool
  , rsAtention :: Bool
  , rsStop :: Bool
  , rsNoGo :: Bool
  }
type RatingStateMutator
  = RatingState -> RatingState

initialReportRatingState :: RatingState
initialReportRatingState = RatingState True True True True -- everything is possible

removeRatingFromState :: Rating -> RatingStateMutator
removeRatingFromState RGo       rs = rs{rsGo = False}
removeRatingFromState RAtention rs = rs{rsAtention = False}
removeRatingFromState RStop     rs = rs{rsStop = False}
removeRatingFromState RNoGo     rs = rs{rsNoGo = False}
removeRatingFromState _         rs = rs -- TODO??

setRatingOfState :: Rating -> RatingStateMutator
setRatingOfState RGo       = removeRatingFromState RAtention . removeRatingFromState RStop . removeRatingFromState RNoGo
setRatingOfState RAtention = removeRatingFromState RGo . removeRatingFromState RStop . removeRatingFromState RNoGo
setRatingOfState RStop     = removeRatingFromState RGo . removeRatingFromState RAtention . removeRatingFromState RNoGo
setRatingOfState RNoGo     = removeRatingFromState RGo . removeRatingFromState RAtention . removeRatingFromState RStop
setRatingOfState _         = removeRatingFromState RGo . removeRatingFromState RAtention . removeRatingFromState RStop . removeRatingFromState RNoGo -- TODO??

ratingFromRatingState :: RatingState -> Rating
ratingFromRatingState rs = let
    mapFromState :: (RatingState -> Bool) -> Rating -> RatingState -> Maybe Rating
    mapFromState getter result state = if getter state
                                       then Just result
                                       else Nothing
    ratingFromSetOfRatings :: [Rating] -> Rating
    ratingFromSetOfRatings [r] = r
    ratingFromSetOfRatings rs' = RUnknown rs'
  in ratingFromSetOfRatings . catMaybes $ map (\f -> f rs) [ mapFromState rsGo RGo
                                                           , mapFromState rsAtention RAtention
                                                           , mapFromState rsStop RStop
                                                           , mapFromState rsNoGo RNoGo
                                                           ]

type RatingRuleFun
  = Statements -> RatingStateMutator
data RatingRule
  = RatingRule
  { rrDescription :: Text
  , rrFunction :: RatingRuleFun
  }
instance Show RatingRule where
  show (RatingRule desc _) = T.unpack desc

ruleFunctionFromCondition :: (Statements -> Bool) -> RatingStateMutator -> RatingRuleFun
ruleFunctionFromCondition condition fun l = if condition l
                                            then fun
                                            else id
negativeRuleFunctionFromCondition :: (Statements -> Bool) -> RatingStateMutator -> RatingRuleFun
negativeRuleFunctionFromCondition condition = ruleFunctionFromCondition (not . condition)

applyRatingRules :: [RatingRule] -> Statements -> Rating
applyRatingRules rrs stmts = let
    applyRatingRules' :: [RatingRule] -> RatingState
    applyRatingRules' = foldr (`rrFunction` stmts) initialReportRatingState
  in ratingFromRatingState (applyRatingRules' rrs)

