{-# LANGUAGE CPP               #-}
{-# LANGUAGE LambdaCase        #-}
{-# LANGUAGE OverloadedStrings #-}
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
import qualified System.CPUTime (getCPUTime)
import qualified Data.Aeson as A


import           Ldbcollector.Model.LicenseFact
import           Ldbcollector.Model.LicenseGraph
import           Ldbcollector.Model.LicenseName
import System.CPUTime (getCPUTime)

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

focusSequentially :: [G.Node] -> LicenseGraph -> (LicenseGraph, ([G.Node], [G.Node], [G.Node]))
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
                reachableForNeedle needle = G.reachable needle subGraph ++ G.reachable needle (G.grev subGraph)
            in nub $ concatMap reachableForNeedle needles'
        isLicenseExpandingRelation = (== LGNameRelation Same)
        isFactAndStatementRelation = (`elem` [LGAppliesTo, LGImpliedBy])
        isOtherRelation r = not (isLicenseExpandingRelation r || isFactAndStatementRelation r)

        reachableViaLicenseExpandingRelation = reachableInSubgraph isLicenseExpandingRelation needles
        reachableViaFactAndStatementRelation = reachableInSubgraph isFactAndStatementRelation reachableViaLicenseExpandingRelation
        reachableOtherRelation = reachableInSubgraph isOtherRelation reachableViaLicenseExpandingRelation
        reachable = nub $ reachableViaFactAndStatementRelation <> reachableOtherRelation

        -- -- reachableViaIsLicenseExpandingRelation = reachableInSubgraph isLicenseExpandingRelation needles
        -- reachableViaIsFactAndStatementRelation = reachableInSubgraph (\n -> isLicenseExpandingRelation n || isFactAndStatementRelation n) needles
        -- reachableViaIsOtherRelation = reachableInSubgraph (\n -> isLicenseExpandingRelation n || isOtherRelation n) needles
        -- reachableViaIsLicenseExpandingRelation = V.filter (`elem` reachableViaIsOtherRelation) reachableViaIsFactAndStatementRelation
        -- reachable = mconcat [ reachableViaIsFactAndStatementRelation 
        --                     , reachableViaIsOtherRelation 
        --                     ]

        isReachable n = n `elem` reachable
    in (LicenseGraph {
        _gr = G.nfilter isReachable gr,
        _node_map = Map.filter isReachable node_map,
        _node_map_rev = Map.filterWithKey (\k _ -> isReachable k) node_map_rev,
        _facts = facts
    }, (reachableViaLicenseExpandingRelation,
        filter (not . (`elem` reachableViaLicenseExpandingRelation)) reachableOtherRelation,
        filter (not . (`elem` reachableViaLicenseExpandingRelation)) reachableViaFactAndStatementRelation))

focus :: [SourceRef] -> Vector LicenseGraphNode -> (([G.Node], [G.Node], [G.Node], [G.Node]) -> LicenseGraphM a) -> LicenseGraphM a
focus sources needles inner = do
    debugLog "## freeze graph"
    start <- lift getCPUTime
    debugOrderAndSize
    frozen <- MTL.get
    (a,_) <- (MTL.lift . runLicenseGraphM' frozen) $ do
        unless (null sources) $ do
            debugLog ("## filter sources on " ++ show sources)
            filterSources sources
        infoLog ("## focus on " ++ show needles)
        needleIds <- V.toList <$> getIdsOfNodes needles
        (focusedLicenseGraph, (sameNames, otherNames, statements)) <- MTL.gets (focusSequentially needleIds)
        MTL.put focusedLicenseGraph
        debugOrderAndSize
        debugLog "## work on focused graph"
        inner (needleIds, sameNames, otherNames, statements)
    end <- lift getCPUTime
    let diff = (fromIntegral (end - start) / (10^12)) :: Double
    infoLog ("## done focusing, took " ++ show diff ++ " sec")
    return a

getFocused :: [SourceRef] -> Vector LicenseGraphNode -> LicenseGraphM LicenseGraph
getFocused sources needles = focus sources needles (const MTL.get)


data AliasCluster
    = AliasCluster
    { name :: LicenseName
    , sameNames :: [LicenseName]
    , otherNames :: [LicenseName]
    }
instance ToJSON AliasCluster where
    toJSON (AliasCluster name sameNames otherNames) = 
        A.object [(fromString . show) name A..=  A.object [ "same" A..= sameNames
                                                          , "other" A..= otherNames
                                                          ]
                 ]

getAliasCluster :: ([G.Node], [G.Node], [G.Node]) -> LicenseGraphM AliasCluster
getAliasCluster ([this], sameNameNodes, otherNameNodes) = do
    let graphNodeToLn (Just (LGName ln)) = Just ln
        graphNodeToLn _ = Nothing
    MTL.gets (graphNodeToLn . (`G.lab` this) . _gr) >>= \case
        Just thisName -> do
            sameNames <- catMaybes <$> mapM (\n -> MTL.gets (graphNodeToLn . (`G.lab` n) . _gr)) sameNameNodes
            otherNames <- catMaybes <$> mapM (\n -> MTL.gets (graphNodeToLn . (`G.lab` n) . _gr)) otherNameNodes
            return (AliasCluster thisName sameNames otherNames)
        Nothing -> fail ("failed to compute cluster for " ++ show this)

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
