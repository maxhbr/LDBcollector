{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE OverloadedStrings #-}
module Processors.Rating
    ( Rating (..)
    , removeRatingFromState, setRatingOfState
    , ruleFunctionFromCondition, negativeRuleFunctionFromCondition
    , RatingRule (..), RatingRuleFun
    , applyRatingRules
    -- Rating Configuration
    , mkRatingConfiguration, emptyRatingConfiguration
    , applyRatingConfiguration, applyEmptyRatingConfiguration
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

data Rating
  = RGo -- can be used
  | RAtention -- needs more atention
  | RStop -- needs aproval
  | RNoGo -- can't be used
  | RUnknown [Rating]
  deriving (Show, Generic, Eq)
instance ToJSON Rating
instance FSRaw Rating where
  getStatementLabel _ = "hasCalculatedRating"
  getStatementContent = toJSON

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
    applyRatingRules' = foldr (`rrFunction` stmts) initialReportRatingState
  in ratingFromRatingState (applyRatingRules' rrs)

{-
 - RatingConfiguration
 -}

data RatingConfiguration
  = RatingConfiguration (Map LicenseName Rating) -- Overwrites
                        [RatingRule] -- ratingRules

mkRatingConfiguration :: (Map LicenseName Rating) -> RatingConfiguration
mkRatingConfiguration rOs = let
    actualRatingRules :: [RatingRule]
    actualRatingRules = let
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

  in RatingConfiguration rOs actualRatingRules

emptyRatingConfiguration :: RatingConfiguration
emptyRatingConfiguration = mkRatingConfiguration M.empty

applyRatingConfiguration :: RatingConfiguration -> (LicenseName, License) -> Rating
applyRatingConfiguration (RatingConfiguration rOs rrs) (ln,l) = let
    calculatedR = applyRatingRules rrs (getStatementsFromLicense l)
  in M.findWithDefault calculatedR ln rOs

applyEmptyRatingConfiguration :: (LicenseName, License) -> Rating
applyEmptyRatingConfiguration = applyRatingConfiguration emptyRatingConfiguration
