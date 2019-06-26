{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE OverloadedStrings #-}
module Model.LicenseProperties.Rating
    where

import qualified Prelude as P
import           MyPrelude

import qualified Text.Pandoc as P
import qualified Text.Pandoc.Builder as P

data Rating
  = RGo -- can be used
  | RAttention -- needs more attention
  | RStop -- needs aproval
  | RNoGo -- can't be used
  | RUnknown [Rating]
  deriving (Generic, Eq)
ratingMoreGeneralThan :: Rating -> Rating -> Bool
ratingMoreGeneralThan widerRating (RUnknown rs)   = all (widerRating `ratingMoreGeneralThan`) rs
ratingMoreGeneralThan (RUnknown rs) smallerRating = any (`ratingMoreGeneralThan` smallerRating) rs
ratingMoreGeneralThan widerRating smallerRating   = widerRating == smallerRating
instance Show Rating where
  show RGo                                       = "Go"
  show RAttention                                 = "Attention"
  show RStop                                     = "Stop"
  show RNoGo                                     = "No-Go"
  show (RUnknown [])                             = "Unknown, no option left"
  show (RUnknown [RGo, RAttention, RStop, RNoGo]) = "Unknown"
  show (RUnknown possibilities)                  = "Unknown, probably " ++ intercalate " or " (map show possibilities)
instance ToJSON Rating
instance Inlineable Rating where
  toInline = P.text . show

-- to keep track of current possibilities
data RatingState
  = RatingState Bool Bool Bool Bool
  | FinalRating Rating
  deriving (Generic, Eq, Show)
instance ToJSON RatingState

rsGo :: RatingState -> Bool
rsGo (RatingState b _ _ _) = b
rsGo (FinalRating r)       = r `ratingMoreGeneralThan` RGo
rsAttention :: RatingState -> Bool
rsAttention (RatingState _ b _ _) = b
rsAttention (FinalRating r)       = r `ratingMoreGeneralThan` RAttention
rsStop :: RatingState -> Bool
rsStop (RatingState _ _ b _) = b
rsStop (FinalRating r)       = r `ratingMoreGeneralThan` RStop
rsNoGo :: RatingState -> Bool
rsNoGo (RatingState _ _ _ b) = b
rsNoGo (FinalRating r)       = r `ratingMoreGeneralThan` RNoGo

ratingFromRatingState :: RatingState -> Rating
ratingFromRatingState s = let
    ratings = [(rsGo, RGo), (rsAttention, RAttention), (rsStop, RStop), (rsNoGo, RNoGo)]
    possibleRatings = catMaybes $ map (\(f,r) -> if f s
                                                 then Just r
                                                 else Nothing) ratings
  in case possibleRatings of
    [r] -> r
    rs  -> RUnknown rs

