{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE OverloadedStrings #-}

module Ldbcollector.Model.OutputLicense
  ( OutputLicense,
    toOutputLicense,
    getOutputLicense,
    getAllOutputLicenses,
    getOutputLicensesByNamespace,
  )
where

import Control.Exception (SomeException, try)
import Control.Monad.State qualified as MTL
import Data.Aeson
import Data.Graph.Inductive.Graph qualified as G
import Data.Text qualified as T
import Data.Vector qualified as V
import Ldbcollector.Model.LicenseFact (LicenseNameCluster (..), getImpliedLicenseTypes)
import Ldbcollector.Model.LicenseGraph (LicenseGraph, LicenseGraphM, LicenseGraphNode (LGFact, LGName), LicenseGraphType, getLicenseGraphLicenseNames, runLicenseGraphM', _gr)
import Ldbcollector.Model.LicenseGraphAlgo (focus, getLicenseNameClusterM)
import Ldbcollector.Model.LicenseName (LicenseName (LicenseName))
import Ldbcollector.Model.LicenseStatement (LicenseType (..))
import MyPrelude

data OutputLicense = OutputLicense
  { licenseNameCluster :: LicenseNameCluster,
    licenseType :: LicenseType
  }

instance ToJSON OutputLicense where
  toJSON (OutputLicense (LicenseNameCluster ln olns olnhs) lt) =
    object
      [ "licenseName" .= ln,
        "otherLicenseNames" .= olns,
        "otherLicenseNameHints" .= olnhs,
        "licenseType" .= show lt,
        "complex" .= object [
          "licenseType" .= lt
        ]
      ]

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

getOutputLicense :: ([G.Node], [G.Node], [G.Node]) -> LicenseGraphM OutputLicense
getOutputLicense (needleNames, sameNames, otherNames) = do
  subgraph <- MTL.gets _gr
  cluster <- getLicenseNameClusterM (needleNames, sameNames, otherNames)
  return (toOutputLicense subgraph cluster)

getAllOutputLicenses :: LicenseGraphM [OutputLicense]
getAllOutputLicenses = do
  allLicenseNames <- MTL.gets getLicenseGraphLicenseNames
  frozen <- MTL.get
  catMaybes . V.toList <$> V.mapM (getOutputLicenseForName frozen) allLicenseNames
  where
    getOutputLicenseForName :: LicenseGraph -> LicenseName -> LicenseGraphM (Maybe OutputLicense)
    getOutputLicenseForName frozen lic = do
      result <-
        lift . try . fmap fst $
          runLicenseGraphM' frozen $
            focus mempty (V.singleton (LGName lic)) $
              \(needleNames, sameNames, otherNames, _statements) -> do
                Just <$> getOutputLicense (needleNames, sameNames, otherNames)
      case result of
        Right ol -> return ol
        Left (_ :: SomeException) -> return Nothing

getOutputLicensesByNamespace :: Text -> LicenseGraphM [OutputLicense]
getOutputLicensesByNamespace ns = do
  allLicenseNames <- MTL.gets getLicenseGraphLicenseNames
  let filteredLicenses =
        V.filter
          ( \case
              LicenseName (Just licNS) name -> licNS == ns && not ("LicenseRef-" `isInfixOf` T.unpack name)
              _ -> False
          )
          allLicenseNames
  frozen <- MTL.get
  catMaybes . V.toList <$> V.mapM (getOutputLicenseForName frozen) filteredLicenses
  where
    getOutputLicenseForName :: LicenseGraph -> LicenseName -> LicenseGraphM (Maybe OutputLicense)
    getOutputLicenseForName frozen lic = do
      result <-
        lift . try . fmap fst $
          runLicenseGraphM' frozen $
            focus mempty (V.singleton (LGName lic)) $
              \(needleNames, sameNames, otherNames, _statements) -> do
                Just <$> getOutputLicense (needleNames, sameNames, otherNames)
      case result of
        Right ol -> return ol
        Left (_ :: SomeException) -> return Nothing
