{-# LANGUAGE ExistentialQuantification #-}
{-# LANGUAGE TypeFamilies #-}
{-# LANGUAGE GADTs #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE DeriveGeneric #-}
module Model.LicenseProperties.Judgement
    where

import qualified Prelude as P
import           MyPrelude

data Judgement
  = PositiveJudgement String
  | NegativeJudgement String
  | NeutralJudgement String
  deriving (Eq, Show, Generic)
instance ToJSON Judgement

instance Ord Judgement where
  compare (PositiveJudgement s1) (PositiveJudgement s2) = s1 `compare` s2
  compare (PositiveJudgement _) _                       = LT
  compare (NeutralJudgement _) (PositiveJudgement _)    = GT
  compare (NeutralJudgement s1) (NeutralJudgement s2)   = s1 `compare` s2
  compare (NeutralJudgement _) _                        = LT
  compare (NegativeJudgement s1) (NegativeJudgement s2) = s1 `compare` s2
  compare (NegativeJudgement _) _                       = GT
