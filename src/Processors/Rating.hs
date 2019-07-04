{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE OverloadedStrings #-}
module Processors.Rating
    ( ratingRules
    , applyRatingRules, applyDefaultRatingRules
    ) where

import qualified Prelude as P
import           MyPrelude

import qualified Data.Text as T
import           Control.Monad.Trans.Writer.Strict (execWriter, tell)
import qualified Data.Map as M

import           Model.License
import           Collectors.BlueOak (blueOakLFC)
import           Collectors.SPDX (spdxLFC)

mergeRaitingStates :: RatingState -> RatingState -> RatingState
mergeRaitingStates rs1@(FinalRating fr1) (FinalRating fr2)             = if fr1 == fr2
                                                                         then rs1
                                                                         else undefined -- TODO
mergeRaitingStates rs1@(FinalRating _) _                               = rs1
mergeRaitingStates _ rs2@(FinalRating _)                               = rs2
mergeRaitingStates (RatingState b1 b2 b3 b4) (RatingState c1 c2 c3 c4) = RatingState (b1 && c1)
                                                                                     (b2 && c2)
                                                                                     (b3 && c3)
                                                                                     (b4 && c4)

type RatingStateMutator
  = RatingState -> RatingState

removeRatingFromState :: Rating -> RatingStateMutator
removeRatingFromState _          rs@(FinalRating _)        = rs -- already final
removeRatingFromState RGo        (RatingState _ b2 b3 b4) = RatingState False b2 b3 b4
removeRatingFromState RAttention (RatingState b1 _ b3 b4) = RatingState b1 False b3 b4
removeRatingFromState RStop      (RatingState b1 b2 _ b4) = RatingState b1 b2 False b4
removeRatingFromState RNoGo      (RatingState b1 b2 b3 _) = RatingState b1 b2 b3 False
removeRatingFromState _          rs             = rs

setRatingOfState :: Rating -> RatingStateMutator
setRatingOfState RGo        = removeRatingFromState RAttention . removeRatingFromState RStop . removeRatingFromState RNoGo
setRatingOfState RAttention = removeRatingFromState RGo . removeRatingFromState RStop . removeRatingFromState RNoGo
setRatingOfState RStop      = removeRatingFromState RGo . removeRatingFromState RAttention . removeRatingFromState RNoGo
setRatingOfState RNoGo      = removeRatingFromState RGo . removeRatingFromState RAttention . removeRatingFromState RStop
setRatingOfState _          = removeRatingFromState RGo . removeRatingFromState RAttention . removeRatingFromState RStop . removeRatingFromState RNoGo -- TODO??
setRatingOfStateIfPossible :: Rating -> RatingStateMutator
setRatingOfStateIfPossible r = \rs -> if ratingIsPossibleInRatingState r rs
                                      then setRatingOfState r rs
                                      else rs

type RatingRuleFun
  = License -> RatingStateMutator
data RatingRule
  = RatingRule
  { rrDescription :: Text
  , rrFunction :: RatingRuleFun
  }
instance Show RatingRule where
  show (RatingRule desc _) = T.unpack desc

applyRatingRules :: [RatingRule] -> License -> Rating
applyRatingRules rrls l = let

    initialReportRatingState :: RatingState
    initialReportRatingState = RatingState True True True True -- everything is possible

    initialImpliedRatingState = case unpackSLSR (getImpliedRatingState l) of
      m -> M.foldr mergeRaitingStates initialReportRatingState m -- pessimistic merging

  in ratingFromRatingState $ foldl' (\oldS rrf -> rrf l oldS) initialImpliedRatingState (map rrFunction rrls)

applyDefaultRatingRules :: License -> Rating
applyDefaultRatingRules = applyRatingRules ratingRules

ratingRules :: [RatingRule]
ratingRules = let
    addRule desc fun = tell . (:[]) $ RatingRule desc fun

    hasPossitiveJudgements l = let
        fun b j = b || (case j of
                          PositiveJudgement _ -> True
                          _ -> False)
      in M.foldl' fun False . unpackSLSR $ getImpliedJudgement l
    hasNegativeJudgements l = let
        fun b j = b || (case j of
                          NegativeJudgement _ -> True
                          _ -> False)
      in M.foldl' fun False . unpackSLSR $ getImpliedJudgement l

  in execWriter $ do

    addRule "NonComercial is a no-go" $ \l ->
      case unpackRLSR (getImpliedNonCommercial l) of
        Just True -> setRatingOfState RNoGo
        _         -> id

    addRule "should have at least one positive and no negative rating to be Go" $ \l ->
      if hasPossitiveJudgements l && not (hasNegativeJudgements l)
      then id
      else removeRatingFromState RGo

    addRule "only known NonCopyleft Licenses can be go" $ \l ->
      case getCalculatedCopyleft l of
        Just NoCopyleft -> id
        _ -> removeRatingFromState RGo

    addRule "Fedora bad Rating implies at least Stop" $ \l ->
      case M.lookup blueOakLFC (unpackSLSR $ getImpliedJudgement l) of
        Just (NegativeJudgement _) -> removeRatingFromState RGo . removeRatingFromState RAttention
        _                          -> id

    addRule "only SPDX licenses can be better than Stop" $ \l ->
      if l `containsFactOfClass` spdxLFC
      then id
      else removeRatingFromState RGo . removeRatingFromState RAttention

    addRule "possitive Rating by BlueOak helps, and if no other rating is negative it implies Go" $ \l ->
      case M.lookup blueOakLFC (unpackSLSR $ getImpliedJudgement l) of
        Just (PositiveJudgement _) -> if hasNegativeJudgements l
                                      then removeRatingFromState RNoGo . removeRatingFromState RStop
                                      else setRatingOfStateIfPossible RGo
        Just (NegativeJudgement _) -> removeRatingFromState RGo . removeRatingFromState RAttention
        _                          -> id
