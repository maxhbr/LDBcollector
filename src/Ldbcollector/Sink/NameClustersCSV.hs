{-# LANGUAGE OverloadedStrings #-}

module Ldbcollector.Sink.NameClustersCSV
  ( writeNameClustersCsv,
  )
where

import Data.ByteString.Lazy qualified as BL
import Data.Csv qualified as Csv
import Data.Graph.Inductive.Graph qualified as G
import Data.List (sort)
import Data.Map qualified as Map
import Data.Set qualified as Set
import Ldbcollector.Model

boolField :: Bool -> Text
boolField True = "true"
boolField False = "false"

data NameClusterRow = NameClusterRow
  { _bestName :: LicenseName,
    _alternativeName :: LicenseName,
    _isAutomatic :: Bool
  }

instance Csv.ToNamedRecord NameClusterRow where
  toNamedRecord (NameClusterRow best alt isAuto) =
    Csv.namedRecord
      [ "best" Csv..= licenseNameToText best,
        "alternative" Csv..= licenseNameToText alt,
        "automatic" Csv..= boolField isAuto
      ]

writeNameClustersCsv :: FilePath -> LicenseGraphM ()
writeNameClustersCsv csvPath = do
  infoLog $ "generate " ++ csvPath
  clusters <- getClusters
  licenseNameGraph <- getLicenseNameGraph
  let labNodes = G.labNodes licenseNameGraph
      nodeToName = Map.fromList labNodes
      nameToNode = Map.fromList (map (\(node, name) -> (name, node)) labNodes)
      betterLookup =
        Map.fromListWith
          (<>)
          [ (dst, [srcName])
            | (src, dst, relation) <- G.labEdges licenseNameGraph,
              relation == Better,
              Just srcName <- [Map.lookup src nodeToName]
          ]
      rows = concatMap (clusterToRows nameToNode betterLookup) clusters
      header = Csv.header ["best", "alternative", "automatic"]
  lift $ createParentDirectoryIfNotExists csvPath
  lift $ BL.writeFile csvPath (Csv.encodeByName header rows)

clusterToRows ::
  Map.Map LicenseName G.Node ->
  Map.Map G.Node [LicenseName] ->
  [LicenseName] ->
  [NameClusterRow]
clusterToRows nameToNode betterLookup cluster =
  let best = minimum cluster
      clusterSet = Set.fromList cluster
      sameRows =
        [ NameClusterRow best alt True
          | alt <- sort cluster,
            alt /= best
        ]
      clusterNodes =
        mapMaybe (`Map.lookup` nameToNode) (Set.toList clusterSet)
      impreciseNames =
        Set.fromList $
          concatMap
            (\node -> Map.findWithDefault [] node betterLookup)
            clusterNodes
      impreciseRows =
        [ NameClusterRow best alt False
          | alt <- sort (Set.toList (impreciseNames Set.\\ clusterSet))
        ]
   in sameRows ++ impreciseRows
