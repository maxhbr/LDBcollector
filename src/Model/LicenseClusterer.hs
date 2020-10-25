module Model.LicenseClusterer
  ( getLicensesFromFacts
  , LicenseClusterTree (..)
  ) where

import qualified Prelude as P
import           MyPrelude

import qualified Data.Vector as V
import qualified Data.Map as M
import qualified Data.List as L
import qualified Data.Set as S
import           Data.Set (Set)
import           Data.Char (toUpper)

import           Model.License hiding (getLicenseFromFacts)

data LicenseClusterTree
  = LCTLeaf (Set LicenseName)
  | LCTNode LicenseClusterTree [LicenseClusterTree]
  deriving (Eq)
lctFromName :: LicenseName -> LicenseClusterTree
lctFromName name = LCTLeaf (S.singleton name)
lctToNames :: LicenseClusterTree -> Set LicenseName
lctToNames (LCTLeaf names) = names
lctToNames (LCTNode prev childs) = foldMap lctToNames (prev : childs)
isSubLctOf :: LicenseClusterTree -> LicenseClusterTree -> Bool
isSubLctOf lct1 lct2 = let
      ns1 = lctToNames lct1
      ns2 = lctToNames lct2
    in ns1 `S.isSubsetOf` ns2

getLicensesFromFacts
  :: Vector LicenseName
  -> Facts
  -> Vector (LicenseName, (License, LicenseClusterTree))
getLicensesFromFacts names facts =
  V.map (\name -> (name, getLicenseFromFacts name facts)) names

getLicenseFromFacts
  :: LicenseName
  -> Facts
  -> (License, LicenseClusterTree)
getLicenseFromFacts name facts = let
    initialLicense = License $ V.singleton (mkLicenseShortnameFact name [])
    initialTree = lctFromName name
  in getLicensesFromFacts' name facts (initialLicense, initialTree)

getLicensesFromFacts'
  :: LicenseName
  -> Facts
  -> (License, LicenseClusterTree)
  -> (License, LicenseClusterTree)
getLicensesFromFacts' name facts (prevLic, prevTree) = let
    normalizeSet :: Set LicenseName -> Set LicenseName
    normalizeSet = S.map (L.map toUpper)
    prevNames = normalizeSet $ lctToNames prevTree
    prevNamesFilter fact = let
        impliedNames = normalizeSet . S.fromList $ getImpliedNonambiguousNames fact
      in not (prevNames `S.disjoint` impliedNames)
    factsIntersectingWithNames = V.filter prevNamesFilter facts
    newClusters = (V.toList
                   . V.filter (not . (`isSubLctOf` prevTree))
                   . V.map LCTLeaf
                  . V.map (S.fromList . getImpliedNonambiguousNames))
                  factsIntersectingWithNames
    newTree = LCTNode prevTree newClusters
  in if L.null newClusters
     then (prevLic, prevTree)
     else getLicensesFromFacts' name facts (License factsIntersectingWithNames, newTree)
