{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE OverloadedStrings #-}

module Ldbcollector.Model.OutputLicense
  ( OutputLicense,
    toOutputLicense,
    getOutputLicense,
  )
where

import Control.Monad.State qualified as MTL
import Data.Graph.Inductive.Graph qualified as G
import Data.Text qualified as T
import Ldbcollector.Model.LicenseFact (LicenseNameCluster (..), getImpliedLicenseTypes)
import Ldbcollector.Model.LicenseGraph (LicenseGraphM, LicenseGraphNode (LGFact), LicenseGraphType, _gr)
import Ldbcollector.Model.LicenseGraphAlgo (getLicenseNameClusterM)
import Ldbcollector.Model.LicenseStatement (LicenseType (..))
import MyPrelude

data OutputLicense = OutputLicense
  { licenseNameCluster :: LicenseNameCluster,
    licenseType :: LicenseType
  }

toOutputLicense :: LicenseGraphType -> LicenseNameCluster -> OutputLicense
toOutputLicense subgraph cluster =
  let facts =
        ( mapMaybe
            ( \case
                LGFact f -> Just f
                _ -> Nothing
            )
            . map snd
            . G.labNodes
        )
          subgraph
      allTypes = concatMap getImpliedLicenseTypes facts
      concludedLicenseType = concludeLicenseType allTypes
   in OutputLicense cluster concludedLicenseType
  where
    concludeLicenseType :: [LicenseType] -> LicenseType
    concludeLicenseType [] = UnknownLicenseType Nothing
    concludeLicenseType types =
      let uniqueTypes = nub types
       in case uniqueTypes of
            [single] -> single
            _ -> UnknownLicenseType Nothing

getOutputLicense :: T.Text -> ([G.Node], [G.Node], [G.Node]) -> LicenseGraphM OutputLicense
getOutputLicense licRaw (needleNames, sameNames, otherNames) = do
  subgraph <- MTL.gets _gr
  cluster <- getLicenseNameClusterM (needleNames, sameNames, otherNames)
  return (toOutputLicense subgraph cluster)
