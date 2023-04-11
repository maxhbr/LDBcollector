{-# LANGUAGE CPP        #-}
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


import           Ldbcollector.Model.LicenseFact
import           Ldbcollector.Model.LicenseGraph
import           Ldbcollector.Model.LicenseName

getClusters :: LicenseGraphM [[LicenseName]]
getClusters = do
    lng <- getLicenseNameGraph
    let keepOnlySame (incoming, node, a, outgoing) = let
                incoming' = filter ((== Same) . fst) incoming
                outgoing' = filter ((== Same) . fst) outgoing
                both = nub $ incoming' <> outgoing'
            in Just (both, node, a, both)
        lngOnlySame = G.gfiltermap keepOnlySame lng


        componentNodes = G.scc lngOnlySame
        clusters =  map (mapMaybe (lngOnlySame `G.lab`)) componentNodes
    return clusters

-- ############################################################################

filterSources :: [SourceRef] -> LicenseGraphM ()
filterSources sources = do
    MTL.modify (\lg@(LicenseGraph {_facts=facts}) -> let
             facts' = Map.filterWithKey (\(o,_) _ -> o `elem` sources) facts
        in lg {_facts = facts'})

focusSequentially :: Vector G.Node -> LicenseGraph -> LicenseGraph
focusSequentially needles (LicenseGraph gr node_map node_map_rev facts) = let

        backed = Map.elems facts
        backedNodes = mconcat $ map fst backed
        backedEdges = mconcat $ map snd backed

        onlyBackedFiltermapfun :: G.Context LicenseGraphNode LicenseGraphEdge -> G.MContext LicenseGraphNode LicenseGraphEdge
        onlyBackedFiltermapfun (incoming, node, label, outgoing) = let
                edgeFilterFun :: G.Node -> G.Node -> LicenseGraphEdge -> Bool
                edgeFilterFun a b edgeLabel = let
                        potentialE = (fmap G.toEdge . find (== (a,b,edgeLabel)) . G.labEdges) gr
                    in case potentialE of
                        Just e  -> e `elem` backedEdges
                        Nothing -> False
            in if node `elem` backedNodes
                then Just (filter (\(edgeLabel, a) -> edgeFilterFun a node edgeLabel) incoming, node, label, filter (\(edgeLabel, b) -> edgeFilterFun node b edgeLabel) outgoing)
                else Nothing
        onlyPredicateFiltermapfun :: (LicenseGraphEdge -> Bool) -> G.Context LicenseGraphNode LicenseGraphEdge -> G.MContext LicenseGraphNode LicenseGraphEdge
        onlyPredicateFiltermapfun predicate (incoming, node, a, outgoing) = let
                isFlippable (LGNameRelation Same,_) = True
                isFlippable _                       = False
                incoming' = nub $ filter (\(l,_) -> predicate l) incoming
                outgoing' = nub $ filter (\(l,_) -> predicate l) outgoing
            in Just (incoming' <> filter isFlippable outgoing', node, a, outgoing' <> filter isFlippable incoming')

        reachableInSubgraph predicate needles' = let
                subGraph = G.gfiltermap (\ctx -> case onlyBackedFiltermapfun ctx of
                                             Just ctx' -> onlyPredicateFiltermapfun predicate ctx'
                                             Nothing -> Nothing) gr
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

focus :: [SourceRef] -> Vector LicenseGraphNode -> LicenseGraphM a -> LicenseGraphM a
focus sources needles inner = do
    debugLog "## freeze graph"
    debugOrderAndSize
    frozen <- MTL.get
    (a,_) <- (MTL.lift . runLicenseGraphM' frozen) $ do
        unless (null sources) $ do
            debugLog ("## filter sources on " ++ show sources)
            filterSources sources
        debugLog ("## focus on " ++ show needles)
        needleIds <- getIdsOfNodes needles
        MTL.modify (focusSequentially needleIds)
        debugOrderAndSize
        debugLog "## work on focused graph"
        inner
    debugLog "## done focusing"
    return a

getFocused :: [SourceRef] -> Vector LicenseGraphNode -> LicenseGraphM LicenseGraph
getFocused sources needles = focus sources needles MTL.get

-- -- ############################################################################

condense :: LicenseGraph -> G.Gr LicenseGraphNode ()
condense g = let
        node_map_rev = _node_map_rev g
        nodesToGraphNodes :: [G.Node] -> [LicenseGraphNode]
        nodesToGraphNodes = map (\n -> Map.findWithDefault (LGVec []) n node_map_rev)
        flattenNodes :: [LicenseGraphNode] -> LicenseGraphNode
        flattenNodes [n] = n
        flattenNodes ns  = LGVec ns
    in (G.nmap (flattenNodes . nodesToGraphNodes) . G.condensation . _gr) g

prettyPrintCondensed :: LicenseGraphM ()
prettyPrintCondensed = do
    condensed <- MTL.gets condense
    lift (G.prettyPrint condensed)
