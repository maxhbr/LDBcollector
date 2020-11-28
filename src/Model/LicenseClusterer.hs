module Model.LicenseClusterer
  ( getLicensesFromFacts
  , LicenseClusterTree (..), lctToNames
  ) where

import qualified Prelude as P
import           MyPrelude

import qualified Data.Vector as V
import qualified Data.List as L
import qualified Data.Set as S
import           Data.Set (Set)
import           Data.Char (toUpper, isSpace, isPrint)

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
    initialTree = lctFromName name
  in getLicensesFromFacts' name (mkLicenseShortnameFact name [] `V.cons` facts) initialTree

normalizeSet :: Set LicenseName -> Set LicenseName
normalizeSet = let
    normalizeKey :: LicenseName -> LicenseName
    normalizeKey =
      L.map toUpper -- Case insensitive comparison
      . filter (not . (`elem` "(),")) -- Ignore some chars
      . filter isPrint -- ignore non-printable chars
      . filter (not . isSpace) -- ignore whitespace
  in S.map normalizeKey

getLicensesFromFacts'
  :: LicenseName
  -> Facts
  -> LicenseClusterTree
  -> (License, LicenseClusterTree)
getLicensesFromFacts' name facts prevTree = let

    prevNames = normalizeSet $ lctToNames prevTree

    factsIntersectingWithNames = let
        impliedNames fact = normalizeSet . S.fromList $ getImpliedNonambiguousNames fact
        prevNamesFilter fact = not (prevNames `S.disjoint` impliedNames fact)
      in V.filter prevNamesFilter facts

    newClusters = (V.toList
                   . V.filter (not . (`isSubLctOf` prevTree))
                   . V.map LCTLeaf
                   . V.map (S.fromList . getImpliedNonambiguousNames))
                  factsIntersectingWithNames

    newTree = LCTNode prevTree newClusters

  in if L.null newClusters
     then (License factsIntersectingWithNames, prevTree)
     else getLicensesFromFacts' name facts newTree
