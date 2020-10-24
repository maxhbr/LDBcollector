-- |

module LicenseClusterer
  (getLicensesFromFacts
  ) where

import qualified Prelude as P
import           MyPrelude

import qualified Data.Vector as V
import qualified Data.Map as M
import qualified Data.List as L

import           Model.License as X



getLicensesFromFacts :: Vector LicenseName -> Int -> Map LicenseName [LicenseName] -> Facts -> Vector (LicenseName, License)
getLicensesFromFacts ids 0 mapping facts = V.map (\i -> (i, getLicenseFromFacts i (M.findWithDefault [] i mapping) facts)) ids
getLicensesFromFacts ids i mapping facts = let
    lics = getLicensesFromFacts ids 0 mapping facts
    newMapping = let
        vectorOfTuplesToMap = M.fromList . V.toList
      in vectorOfTuplesToMap $ V.map (\(name,License fs) -> (name, L.nub (concatMap getImpliedNonambiguousNames (V.toList fs)))) lics
  in getLicensesFromFacts ids (i - 1) newMapping facts
