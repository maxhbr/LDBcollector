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


import           Ldbcollector.Model.LicenseName
import           Ldbcollector.Model.LicenseGraph

condense :: LicenseGraph -> G.Gr LicenseGraphNode ()
condense = undefined
-- condense g = let
--         node_map_rev = _node_map_rev g
--         nodesToGraphNodes :: [G.Node] -> [LicenseGraphNode]
--         nodesToGraphNodes = map (\n -> Map.findWithDefault (Vec []) n node_map_rev)
--         flattenNodes :: [LicenseGraphNode] -> LicenseGraphNode
--         flattenNodes [n] = n
--         flattenNodes ns = Vec ns
--     in (G.nmap (flattenNodes . nodesToGraphNodes) . G.condensation . _gr) g

prettyPrintCondensed :: LicenseGraphM ()
prettyPrintCondensed = do
    condensed <- MTL.gets condense
    lift (G.prettyPrint condensed)

-- ############################################################################

focus' :: Vector G.Node -> LicenseGraph -> LicenseGraph
focus' = undefined
-- focus' needles (LicenseGraph gr node_map node_map_rev) = let
--         expandedNeedles = let
--                 licenseNameSubgraph :: LicenseGraphType
--                 licenseNameSubgraph = let
--                         isReversable Same = True
--                         -- isReversable Better = True
--                         isReversable _ = False
--                         isLicenseNameSubgraphEdge (Potentially e, n) = isLicenseNameSubgraphEdge (e, n)
--                         isLicenseNameSubgraphEdge (Better, n) = True
--                         isLicenseNameSubgraphEdge (e, _) = isReversable e
--                         edgeFun = filter isLicenseNameSubgraphEdge
--                         reverseEdges = filter (isReversable . fst)

--                         fun :: G.Context LicenseGraphNode LicenseGraphEdge -> G.MContext LicenseGraphNode LicenseGraphEdge
--                         fun (incoming, node, a@(LicenseName _), outgoing) = let
--                                 filteredIncoming = edgeFun incoming
--                                 filteredOutgoing = edgeFun outgoing
--                                 finalIncoming = nub $ filteredIncoming ++ reverseEdges filteredOutgoing
--                                 finalOutgoing = nub $ filteredOutgoing ++ reverseEdges filteredIncoming
--                             in Just (finalIncoming, node, a, finalOutgoing)
--                         fun _ = Nothing
--                     in G.gfiltermap fun gr
--             in V.concatMap (\needle -> V.fromList $ G.reachable needle (G.grev licenseNameSubgraph)) needles

--         allReachable = let
--                 reachableForNeedle needle = G.reachable needle gr ++ G.reachable needle (G.grev gr)
--             in concatMap reachableForNeedle (V.toList expandedNeedles)
--         isReachable n = n `elem` allReachable
--     in LicenseGraph {
--         _gr = G.nfilter isReachable gr,
--         _node_map = Map.filter isReachable node_map,
--         _node_map_rev = Map.filterWithKey (\k a -> isReachable k) node_map_rev
--     }

-- focus :: Vector LicenseGraphNode -> LicenseGraphM a -> LicenseGraphM a
-- focus needles inner = do
--     stderrLog "get graph"
--     frozen <- MTL.get
--     (a,_) <- (MTL.lift . runLicenseGraphM' frozen) $ do
--         stderrLog "focus graph"
--         needleIds <- addNodes needles
--         MTL.modify (focus' needleIds)
--         stderrLog "work on focused graph"
--         inner
--     stderrLog "end focusing"
--     return a

getFocused :: Vector LicenseGraphNode -> LicenseGraphM LicenseGraph
getFocused needles = undefined -- focus needles MTL.get