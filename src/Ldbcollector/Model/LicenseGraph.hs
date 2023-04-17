{-# LANGUAGE GADTs             #-}
{-# LANGUAGE LambdaCase        #-}
{-# LANGUAGE OverloadedStrings #-}
module Ldbcollector.Model.LicenseGraph
  where

import           MyPrelude

import qualified Control.Monad.State                 as MTL
import qualified Data.Graph.Inductive.Graph          as G
import qualified Data.Graph.Inductive.PatriciaTree   as G
import qualified Data.Map                            as Map
import qualified Data.Set                            as Set
import qualified Data.Vector                         as V

import qualified Control.Monad.Reader                as MTL
import           Ldbcollector.Model.LicenseFact
import           Ldbcollector.Model.LicenseName
import           Ldbcollector.Model.LicenseStatement

-- ############################################################################

debugLog :: String -> LicenseGraphM ()
debugLog = MTL.liftIO . debugLogIO
logFileRead :: String -> LicenseGraphM ()
logFileRead = MTL.liftIO . logFileReadIO
infoLog :: String -> LicenseGraphM ()
infoLog = MTL.liftIO . infoLogIO
stderrLog :: String -> LicenseGraphM ()
stderrLog = MTL.liftIO . stderrLogIO

-- ############################################################################

data LicenseGraphNode where
    LGName        :: LicenseName -> LicenseGraphNode
    LGStatement   :: LicenseStatement -> LicenseGraphNode
    LGLicenseText :: Text -> LicenseGraphNode
    LGFact        :: LicenseFact -> LicenseGraphNode
    LGVec         :: [LicenseGraphNode] -> LicenseGraphNode
deriving instance Show LicenseGraphNode
deriving instance Eq LicenseGraphNode
deriving instance Ord LicenseGraphNode

data LicenseGraphEdge where
    LGNameRelation :: LicenseNameRelation -> LicenseGraphEdge
    LGAppliesTo    :: LicenseGraphEdge
    LGImpliedBy    :: LicenseGraphEdge
deriving instance Show LicenseGraphEdge
deriving instance Eq LicenseGraphEdge

type LicenseGraphType = G.Gr LicenseGraphNode LicenseGraphEdge

data LicenseGraph
    = LicenseGraph
    { _gr           :: LicenseGraphType
    , _node_map     :: Map.Map LicenseGraphNode G.Node
    , _node_map_rev :: Map.Map G.Node LicenseGraphNode
    , _facts        :: Map.Map (SourceRef, LicenseFact) (Set.Set G.Node, Set.Set G.Edge)
    }
emptyLG :: LicenseGraph
emptyLG = LicenseGraph G.empty mempty mempty mempty
instance Show LicenseGraph where
    show = G.prettify . _gr

getLicenseGraphSize :: LicenseGraph -> Int
getLicenseGraphSize (LicenseGraph gr node_map node_map_rev _) = let
        gr_size = length $ G.nodes gr
        node_map_size = Map.size node_map
        node_map_rev_size =  Map.size node_map_rev
    in gr_size

getLicenseGraphLicenseNames :: LicenseGraph -> Vector LicenseName
getLicenseGraphLicenseNames = let
        fun (LGName ln) = [ln]
        fun _           = []
    in V.fromList . concatMap (fun . snd) . G.labNodes . _gr

type LicenseGraphM a = MTL.StateT LicenseGraph IO a
runLicenseGraphM' :: LicenseGraph -> LicenseGraphM a -> IO (a, LicenseGraph)
runLicenseGraphM' initGraph = (`MTL.runStateT` initGraph)
runLicenseGraphM :: LicenseGraphM a -> IO (a, LicenseGraph)
runLicenseGraphM = runLicenseGraphM' emptyLG

type WithFactM a = MTL.ReaderT (SourceRef, LicenseFact) (MTL.StateT LicenseGraph IO) a
withFact :: (SourceRef,LicenseFact) -> WithFactM a -> LicenseGraphM a
withFact key = (`MTL.runReaderT` key)

getIdOfNode :: LicenseGraphNode -> LicenseGraphM (Maybe G.Node)
getIdOfNode lgn = MTL.gets ((lgn `Map.lookup`) . _node_map)

getIdsOfNodes :: V.Vector LicenseGraphNode -> LicenseGraphM (V.Vector G.Node)
getIdsOfNodes lgns = V.catMaybes <$> mapM getIdOfNode lgns

insertNode' ::  LicenseGraphNode -> LicenseGraphM G.Node
insertNode' lgn = getIdOfNode lgn >>= \case
  Just n  -> return n
  Nothing -> do
    n <- MTL.gets ((+ 1) . G.noNodes . _gr)
    MTL.modify (\graph -> graph { _gr           = G.insNode (n, lgn) (_gr graph)
                                , _node_map     = Map.insert lgn n (_node_map graph)
                                , _node_map_rev = Map.insert n lgn (_node_map_rev graph)
                                }
               )
    return n

insertNode :: LicenseGraphNode -> WithFactM G.Node
insertNode lgn = do
    n <- lift $ insertNode' lgn
    key <- MTL.ask
    MTL.modify (\graph -> graph { _facts = Map.insertWith (\(ns,es) (ns', es') -> (ns<>ns', es<>es'))
                                                          key
                                                          (Set.singleton n, mempty)
                                                          (_facts graph)
                                }
               )
    return n
insertNodes :: Vector LicenseGraphNode -> WithFactM (Vector G.Node)
insertNodes = V.mapM insertNode

isAllowedLEdge :: G.LEdge LicenseGraphEdge -> LicenseGraphM Bool
isAllowedLEdge (a, b, LGNameRelation _) = do
    an <- MTL.gets ((a `Map.lookup`) . _node_map_rev)
    bn <- MTL.gets ((b `Map.lookup`) . _node_map_rev)
    return $ case an of
                Just (LGName _) ->
                    case bn of
                        Just (LGName _) -> True
                        _               -> False
                _ -> False
isAllowedLEdge (a, b, LGAppliesTo) = do
    an <- MTL.gets ((a `Map.lookup`) . _node_map_rev)
    bn <- MTL.gets ((b `Map.lookup`) . _node_map_rev)
    return $ case an of
                Just (LGFact _) ->
                    case bn of
                        Just (LGName _) -> True
                        _               -> False
                _ -> False
isAllowedLEdge (a, b, LGImpliedBy) = do
    an <- MTL.gets ((a `Map.lookup`) . _node_map_rev)
    bn <- MTL.gets ((b `Map.lookup`) . _node_map_rev)
    return $ case an of
                Just (LGStatement _) ->
                    case bn of
                        Just (LGFact _)      -> True
                        Just (LGStatement _) -> True
                        _                    -> False
                Just (LGLicenseText _) ->
                    case bn of
                        Just (LGFact _) -> True
                        _               -> False
                _ -> False

insertEdge :: (LicenseGraphNode, LicenseGraphNode, LicenseGraphEdge) -> WithFactM G.Node
insertEdge = let
        insertLEdge :: G.LEdge LicenseGraphEdge -> WithFactM ()
        insertLEdge edge = do
            isAllowed <- MTL.lift $ isAllowedLEdge edge
            unless isAllowed $ fail ("tried to add not allowed edge: " ++ show edge)

            alreadyHasTheEdge <- MTL.gets ((`G.hasLEdge` edge) . _gr)
            unless alreadyHasTheEdge $
                MTL.modify (\state -> state { _gr = edge `G.insEdge` _gr state })
            potentialE <- MTL.gets (fmap G.toEdge . find (== edge) . G.labEdges . _gr)
            case potentialE of
                Just e -> do
                    key <- MTL.ask
                    MTL.modify (\graph -> graph { _facts = Map.insertWith (\(ns,es) (ns', es') -> (ns<>ns', es<>es'))
                                                                          key
                                                                          (mempty, Set.singleton e)
                                                                          (_facts graph)
                                                }
                               )
                Nothing -> pure ()
    in \(a,b,e) -> do
        na <- insertNode a
        nb <- insertNode b
        unless (na == nb) $ do
            insertLEdge (na, nb, e)
            -- when (e == LGNameRelation Same) $
            --     insertLEdge (nb, na, e)
        return na
insertEdges :: Vector (LicenseGraphNode, LicenseGraphNode, LicenseGraphEdge) -> WithFactM (Vector G.Node)
insertEdges = V.mapM insertEdge

applyFact :: WithFactM G.Node
applyFact = do
    fact <- MTL.asks snd
    let factLG = LGFact fact
    factNode <- insertNode (LGFact fact)
    lnNode <- applyFactApplicableLNs (getApplicableLNs fact)
    _ <- insertEdge (factLG, lnNode, LGAppliesTo)
    stmtNodes <- applyFactImpliedStmts (filterStatements $ getImpliedStmts fact)
    let edges = V.fromList $ map (,factLG, LGImpliedBy) stmtNodes
    _ <- insertEdges edges
    return factNode

applyFactApplicableLNs :: ApplicableLNs -> WithFactM LicenseGraphNode
applyFactApplicableLNs (LN ln) = let
      node = LGName ln
      namespacelessNode = LGName (unsetNS ln)
    in do
        _ <- insertNode node
        unless (node == namespacelessNode) $ do
            _ <- insertNode namespacelessNode
            _ <- insertEdge (namespacelessNode, node, LGNameRelation Same)
            pure ()
        return node
applyFactApplicableLNs (ln `AlternativeLNs` alns) = do
    node <- applyFactApplicableLNs ln
    alnNodes <- mapM applyFactApplicableLNs alns
    let edges = map (,node,LGNameRelation Same) alnNodes
    _ <- insertEdges (V.fromList edges)
    return node
applyFactApplicableLNs (ln `ImpreciseLNs` alns) = do
    node <- applyFactApplicableLNs ln
    alnNodes <- mapM applyFactApplicableLNs alns
    let edges = map (,node,LGNameRelation Better) alnNodes
    _ <- insertEdges (V.fromList edges)
    return node

applyFactImpliedStmts :: [LicenseStatement] -> WithFactM [LicenseGraphNode]
applyFactImpliedStmts stmts = mconcat <$> mapM applyFactImpliedStmt stmts

applyFactImpliedStmt :: LicenseStatement -> WithFactM [LicenseGraphNode]
applyFactImpliedStmt (stmt `SubStatements` stmts) = do
    nodes <- applyFactImpliedStmt stmt
    nodes' <- mconcat <$> mapM applyFactImpliedStmt stmts
    let edges = V.fromList $ concatMap (\node -> map (, node, LGImpliedBy) nodes') nodes
    _ <- insertEdges edges
    return nodes
applyFactImpliedStmt (MaybeStatement (Just stmt)) = applyFactImpliedStmt stmt
applyFactImpliedStmt (MaybeStatement Nothing) = pure []
applyFactImpliedStmt stmt = do
    let stmtLG = LGStatement stmt
    _ <- insertNode stmtLG
    return [stmtLG]

debugOrderAndSize :: LicenseGraphM ()
debugOrderAndSize = do
    order <- MTL.gets (G.order . _gr)
    size <- MTL.gets (G.size . _gr)
    debugLog ("order=" ++ show order ++ " size=" ++ show size)

-- ############################################################################


type LicenseNameGraphType = G.Gr LicenseName LicenseNameRelation

toLicenseNameGraph :: LicenseGraphType -> LicenseNameGraphType
toLicenseNameGraph = let
        edgeFun :: (LicenseGraphEdge, G.Node) -> Maybe (LicenseNameRelation, G.Node)
        edgeFun (LGNameRelation nr, n) = Just (nr, n)
        edgeFun _                      = Nothing
        contextFun :: G.Context LicenseGraphNode LicenseGraphEdge -> G.MContext LicenseName LicenseNameRelation
        contextFun (incoming, n, LGName ln, outgoing) = let
                incoming' = nub $ mapMaybe edgeFun incoming
                outgoing' = nub $ mapMaybe edgeFun outgoing
            in Just (incoming', n, ln, outgoing')
        contextFun _ = Nothing
    in G.gfiltermap contextFun

getLicenseNameGraph :: LicenseGraphM LicenseNameGraphType
getLicenseNameGraph = MTL.gets (toLicenseNameGraph . _gr)
