{-# LANGUAGE LambdaCase #-}
module Ldbcollector.Model.LicenseGraphAlgo
  where
--   ( focus
--   , getFocused
--   ) where

import           MyPrelude

import qualified Control.Monad.State               as MTL
import qualified Data.Graph.Inductive.Basic        as G
import qualified Data.Graph.Inductive.Graph        as G
import qualified Data.Graph.Inductive.PatriciaTree as G
import qualified Data.Graph.Inductive.Query.DFS    as G
import qualified Data.Map                          as Map
import qualified Data.Vector                       as V


import           Ldbcollector.Model.LicenseGraph
import           Ldbcollector.Model.LicenseName

getClusters :: LicenseGraphM [[LicenseName]]
getClusters = do
    lng <- getLicenseNameGraph
    node_map_rev <- MTL.gets _node_map_rev
    let keepOnlySame (incoming, node, a, outgoing) = let
            incoming' = filter ((== Same) . fst) incoming
            outgoing' = filter ((== Same) . fst) outgoing
            both = nub $ incoming' <> outgoing'
          in Just (both, node, a, both)
        lngOnlySame = G.gfiltermap keepOnlySame lng 
        componentNodes = G.scc lngOnlySame

        nodesToGraphNodes = map (\n -> case lngOnlySame `G.lab` n of
                                            Just name -> name
                                            _ -> undefined)
                                        
        condensed = (G.nmap nodesToGraphNodes . G.condensation) lngOnlySame
        clusters = (map snd . G.labNodes) condensed
    return clusters
    -- return $ map (mapMaybe (\case
    --                             LGName n -> Just n
    --                             _ -> Nothing) . mapMaybe (`Map.lookup` node_map_rev)) componentNodes

-- ############################################################################

focusSequentially :: Vector G.Node -> LicenseGraph -> LicenseGraph
focusSequentially needles (LicenseGraph gr node_map node_map_rev facts) = let
        reachableInSubgraph predicate needles' = let
                isFlippable (LGNameRelation Same,_) = True
                isFlippable _ = False
                fun :: G.Context LicenseGraphNode LicenseGraphEdge -> G.MContext LicenseGraphNode LicenseGraphEdge
                fun (incoming, node, a, outgoing) = let
                        incoming' = nub $ filter (\(l,_) -> predicate l) incoming
                        outgoing' = nub $ filter (\(l,_) -> predicate l) outgoing
                    in Just (incoming' <> filter isFlippable outgoing', node, a, outgoing' <> filter isFlippable incoming')
                subGraph = G.gfiltermap fun gr
                reachableForNeedle needle = V.fromList $ G.reachable needle subGraph ++ G.reachable needle (G.grev subGraph)
            in V.concatMap reachableForNeedle needles'
        isLicenseExpandingRelation = (== LGNameRelation Same)
        isFactAndStatementRelation = (`elem` [LGAppliesTo, LGImpliedBy])
        isOtherRelation r = not (isLicenseExpandingRelation r || isFactAndStatementRelation r) 
        reachable = (reachableInSubgraph isOtherRelation . reachableInSubgraph isFactAndStatementRelation . reachableInSubgraph isLicenseExpandingRelation) needles
        isReachable n = n `elem` reachable
    in LicenseGraph {
        _gr = G.nfilter isReachable gr,
        _node_map = Map.filter isReachable node_map,
        _node_map_rev = Map.filterWithKey (\k _ -> isReachable k) node_map_rev,
        _facts = facts
    }

focus' :: Vector G.Node -> LicenseGraph -> LicenseGraph
focus' needles (LicenseGraph gr node_map node_map_rev facts) = let
        allReachable = let
                reachableForNeedle needle = G.reachable needle gr ++ G.reachable needle (G.grev gr)
            in concatMap reachableForNeedle (V.toList needles)
        isReachable n = n `elem` allReachable
    in LicenseGraph {
        _gr = G.nfilter isReachable gr,
        _node_map = Map.filter isReachable node_map,
        _node_map_rev = Map.filterWithKey (\k _ -> isReachable k) node_map_rev,
        _facts = facts
    }

focus :: Vector LicenseGraphNode -> LicenseGraphM a -> LicenseGraphM a
focus needles inner = do
    stderrLog "get graph"
    frozen <- MTL.get
    (a,_) <- (MTL.lift . runLicenseGraphM' frozen) $ do
        stderrLog "focus graph"
        needleIds <- getIdsOfNodes needles
        MTL.modify (focusSequentially needleIds)
        stderrLog "work on focused graph"
        inner
    stderrLog "end focusing"
    return a

getFocused :: Vector LicenseGraphNode -> LicenseGraphM LicenseGraph
getFocused needles = focus needles MTL.get

-- ############################################################################

condense :: LicenseGraph -> G.Gr LicenseGraphNode ()
condense g = let
        node_map_rev = _node_map_rev g
        nodesToGraphNodes :: [G.Node] -> [LicenseGraphNode]
        nodesToGraphNodes = map (\n -> Map.findWithDefault (LGVec []) n node_map_rev)
        flattenNodes :: [LicenseGraphNode] -> LicenseGraphNode
        flattenNodes [n] = n
        flattenNodes ns = LGVec ns
    in (G.nmap (flattenNodes . nodesToGraphNodes) . G.condensation . _gr) g

prettyPrintCondensed :: LicenseGraphM ()
prettyPrintCondensed = do
    condensed <- MTL.gets condense
    lift (G.prettyPrint condensed)
