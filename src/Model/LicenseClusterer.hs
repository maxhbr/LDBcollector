module Model.LicenseClusterer
  ( getLicensesFromFacts
  , LicenseClusterTree
  ) where

import qualified Prelude as P
import           MyPrelude

import qualified Data.Vector as V
import qualified Data.Map as M
import qualified Data.List as L
import           Data.PartialOrd (PartialOrd ((<=)))
import           Data.Set as S
import           Data.Char (toUpper)

import           Model.License as X hiding (getLicenseFromFacts)

data LicenseClusterTree
  = LCTLeaf (Set LicenseName)
  | LCTNode LicenseClusterTree [LicenseClusterTree]
  deriving (Eq)
instance Show LicenseClusterTree where
  show (LCTLeaf names) = "{" ++ (L.intercalate ", " (L.map show (S.toList names))) ++ "}"
  show (LCTNode prev childs) = "{" ++ (L.intercalate ", " (L.map show (prev: childs))) ++ "}"
lctFromName :: LicenseName -> LicenseClusterTree
lctFromName name = LCTLeaf (S.singleton name)
lctFromNames :: [LicenseName] -> LicenseClusterTree
lctFromNames names = LCTLeaf (S.fromList names)
lctToNames :: LicenseClusterTree -> Set LicenseName
lctToNames (LCTLeaf names) = names
lctToNames (LCTNode prev childs) = (foldMap lctToNames (prev : childs))
instance PartialOrd LicenseClusterTree where
  lct1 <= lct2 = let
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
                   . (V.map LCTLeaf)
                   . (V.filter (\set -> not ((normalizeSet set) `S.isSubsetOf` prevNames)))
                  . (V.map (S.fromList . getImpliedNonambiguousNames)))
                  factsIntersectingWithNames
    newTree = LCTNode prevTree newClusters
  in if (L.null newClusters)
     then (prevLic, prevTree)
     else getLicensesFromFacts' name facts (License factsIntersectingWithNames, newTree)
