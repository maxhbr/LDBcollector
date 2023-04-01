{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE GADTs #-}
module Ldbcollector.Model.LicenseGraph
  where
--   ( LicenseGraphNode (..)
--   , mkLGValue, isEmptyLGN
--   , LicenseGraphEdge (..)
--   , LicenseGraph (..), LicenseGraphType
--   , getLicenseGraphLicenseNames
--   , getLicenseGraphSize
--   , LicenseGraphM
--   , runLicenseGraphM, runLicenseGraphM'
--   , addNode, addNodes
--   , addEdge, addEdges
--   , stderrLog
--   ) where

import           MyPrelude

import qualified Control.Monad.State               as MTL
import           Data.Aeson                        as A
import           Data.Aeson.Encode.Pretty          as A
import qualified Data.ByteString.Char8             as B (unpack)
import qualified Data.ByteString.Lazy              as BL (toStrict)
import qualified Data.Graph.Inductive.Graph        as G
import qualified Data.Graph.Inductive.PatriciaTree as G
import qualified Data.Map                          as Map
import qualified Data.Set                          as Set
import qualified Data.Vector                       as V
import           System.Console.Pretty             (Color (Green), color)

import           Ldbcollector.Model.LicenseName
import           Ldbcollector.Model.LicenseStatement
import           Ldbcollector.Model.LicenseFact
import qualified Control.Monad.Reader as MTL

-- ############################################################################

stderrLog :: String -> LicenseGraphM ()
stderrLog msg = MTL.liftIO $ hPutStrLn stderr (color Green msg)

-- ############################################################################

data LicenseGraphNode where
    LGName      :: LicenseName -> LicenseGraphNode
    LGStatement :: LicenseStatement -> LicenseGraphNode
    LGFact      :: LicenseFact -> LicenseGraphNode
deriving instance Show LicenseGraphNode
deriving instance Eq LicenseGraphNode
deriving instance Ord LicenseGraphNode

data LicenseGraphEdge where
    LGNameRelation :: LicenseNameRelation -> LicenseGraphEdge
    LGAppliesTo    :: LicenseGraphEdge
    LGImpliedBy      :: LicenseGraphEdge
deriving instance Show LicenseGraphEdge
deriving instance Eq LicenseGraphEdge

type LicenseGraphType = G.Gr LicenseGraphNode LicenseGraphEdge

data LicenseGraph
    = LicenseGraph
    { _gr           :: G.Gr LicenseGraphNode LicenseGraphEdge
    , _node_map     :: Map.Map LicenseGraphNode G.Node
    , _node_map_rev :: Map.Map G.Node LicenseGraphNode
    , _facts        :: Map.Map (Origin, LicenseFact) (Set.Set G.Node, Set.Set G.Edge)
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
        fun _ = []
    in V.fromList . concatMap (fun . snd) . G.labNodes . _gr

type LicenseGraphM a = MTL.StateT LicenseGraph IO a
runLicenseGraphM' :: LicenseGraph -> LicenseGraphM a -> IO (a, LicenseGraph)
runLicenseGraphM' initGraph = (`MTL.runStateT` initGraph)
runLicenseGraphM :: LicenseGraphM a -> IO (a, LicenseGraph)
runLicenseGraphM = runLicenseGraphM' emptyLG

type WithFactM a = MTL.ReaderT (Origin, LicenseFact) (MTL.StateT LicenseGraph IO) a
withFact :: (Origin,LicenseFact) -> WithFactM a -> LicenseGraphM a
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
                        _ -> False
                _ -> False
isAllowedLEdge (a, b, LGAppliesTo) = do
    an <- MTL.gets ((a `Map.lookup`) . _node_map_rev)
    bn <- MTL.gets ((b `Map.lookup`) . _node_map_rev)
    return $ case an of
                Just (LGStatement _) ->
                    case bn of
                        Just (LGName _) -> True
                        Just (LGStatement _) -> True
                        _ -> False
                _ -> False
isAllowedLEdge (a, b, LGImpliedBy) = do
    an <- MTL.gets ((a `Map.lookup`) . _node_map_rev)
    bn <- MTL.gets ((b `Map.lookup`) . _node_map_rev)
    return $ case an of
                Just (LGStatement _) -> 
                    case bn of
                        Just (LGFact _) -> True
                        _ -> False
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
            when (e == LGNameRelation Same) $
                insertLEdge (nb, na, e)
        return na
insertEdges :: Vector (LicenseGraphNode, LicenseGraphNode, LicenseGraphEdge) -> WithFactM (Vector G.Node)
insertEdges = V.mapM insertEdge

insertImpliedByFact :: LicenseGraphNode -> WithFactM (G.Node, G.Node)
insertImpliedByFact lgn = do
    lgnNode <- insertNode lgn 
    factLG <- MTL.asks (LGFact . snd)
    factNode <- insertNode factLG
    void $ insertEdge (lgn, factLG, LGImpliedBy)
    return (lgnNode, factNode)

applyEdgeTask :: LicenseFactTask -> LicenseGraphEdge -> LicenseFactTask -> WithFactM (Vector LicenseGraphNode, Vector LicenseGraphNode)
applyEdgeTask left edge right = do
    leftNodes <- applyTask' left
    rightNodes <- applyTask' right
    let pairs = liftM2 (,) leftNodes rightNodes
    let edges = V.map (\(leftNode,rightNode) -> (leftNode,rightNode,edge)) pairs
    _ <- insertEdges edges
    return (leftNodes, rightNodes)

applyLnRelation ::  [LicenseName] -> LicenseFactTask -> LicenseNameRelation  -> WithFactM (Vector LicenseGraphNode)
applyLnRelation lefts rightTask relation = do
    rNodes <- applyTask' rightTask
    lNodes <- mconcat <$> mapM (applyTask' . AddLN) lefts
    let edges = V.concatMap (\tNode -> V.map (,tNode, LGNameRelation relation) lNodes) rNodes
    _ <- insertEdges edges
    return lNodes

applyTask' :: LicenseFactTask -> WithFactM (Vector LicenseGraphNode)
applyTask' Noop = pure mempty
applyTask' (AllTs ts) = mconcat <$> mapM applyTask' ts
applyTask' (AddLN ln) = let
      node = LGName ln
    in insertNode node >> return (V.singleton node)
applyTask' (SameLNs sames t) = applyLnRelation sames t Same
applyTask' (BetterLNs sames t) = applyLnRelation sames t Better
applyTask' (AppliesToLN stmt ln) = do
    let stmtLG = LGStatement stmt
    (stmtNode, factNode) <- insertImpliedByFact stmtLG
    lNodes <- applyTask' (AddLN ln)
    let edges = V.map (stmtLG, , LGAppliesTo) lNodes
    _ <- insertEdges edges
    return lNodes
applyTask' (MAppliesToLN (Just stmt) ln) = applyTask' (AppliesToLN stmt ln)
applyTask' (MAppliesToLN Nothing ln) = do
    applyTask' (AddLN ln)
    return mempty

applyTask :: LicenseFactTask -> WithFactM ()
applyTask = void . applyTask'













{-
data LicenseGraphNode where
    -- LGVec       :: [LicenseGraphNode] -> LicenseGraphNode

    LGName      :: LicenseName -> LicenseGraphNode
    LGFact     :: LicenseFact -> LicenseGraphNode
    LGStatement :: LicenseStatement -> LicenseGraphNode
deriving instance Eq LicenseGraphNode
deriving instance Ord LicenseGraphNode
instance Show LicenseGraphNode where
    show (LGVec v)       = show v
    show (LGName ln)     = show ln
    show (LGStatement d) = unpack d
    show (LGValue v)     = B.unpack . BL.toStrict $ A.encodePretty v
mkLGValue :: (Typeable a, ToJSON a) => a -> LicenseGraphNode
mkLGValue a = LGValue (WrappedValue (typeOf a) a)
isEmptyLGN :: LicenseGraphNode -> Bool
isEmptyLGN (LGVec [])   = True
isEmptyLGN (LGVec lgns) = all isEmptyLGN lgns
isEmptyLGN (LGValue v)  = toJSON v == A.Null
isEmptyLGN _            = False
instance IsString LicenseGraphNode where
    fromString s = LGStatement (pack s)
data LicenseGraphEdge where
    Same        :: LicenseGraphEdge
    Better      :: LicenseGraphEdge
    AppliesTo   :: LicenseGraphEdge
    Potentially :: LicenseGraphEdge -> LicenseGraphEdge
    deriving (Show, Eq, Ord)

type LicenseGraphType = G.Gr LicenseGraphNode LicenseGraphEdge
data LicenseGraph
    = LicenseGraph
    { _gr           :: G.Gr LicenseGraphNode LicenseGraphEdge
    , _node_map     :: Map.Map LicenseGraphNode G.Node
    , _node_map_rev :: Map.Map G.Node LicenseGraphNode
    }
instance Show LicenseGraph where
    show (LicenseGraph gr _ _) = G.prettify gr
getSameSubgraph :: LicenseGraph -> LicenseGraphType
getSameSubgraph (LicenseGraph {_gr = gr}) = gr

getLicenseGraphSize :: LicenseGraph -> Int
getLicenseGraphSize (LicenseGraph gr node_map node_map_rev) = let
        gr_size = length $ G.nodes gr
        node_map_size = Map.size node_map
        node_map_rev_size =  Map.size node_map_rev
    in gr_size

getLicenseGraphLicenseNames :: LicenseGraph -> Vector LicenseName
getLicenseGraphLicenseNames = let
        fun (LGName ln) = [ln]
        fun _ = []
    in V.fromList . concatMap (fun . snd) . G.labNodes . _gr

type LicenseGraphM a = MTL.StateT LicenseGraph IO a

runLicenseGraphM' :: LicenseGraph -> LicenseGraphM a -> IO (a, LicenseGraph)
runLicenseGraphM' initGraph = (`MTL.runStateT` initGraph)

runLicenseGraphM :: LicenseGraphM a -> IO (a, LicenseGraph)
runLicenseGraphM = runLicenseGraphM' $ LicenseGraph G.empty mempty mempty

addNode :: LicenseGraphNode -> LicenseGraphM G.Node
addNode = let
        getUnusedNode :: LicenseGraphM G.Node
        getUnusedNode = MTL.gets ((+ 1) . G.noNodes . _gr)

        insertLNode :: G.LNode LicenseGraphNode -> LicenseGraphM ()
        insertLNode (n, lgn) = MTL.modify
            (\state -> state
                { _gr           = G.insNode (n, lgn) (_gr state)
                , _node_map     = Map.insert lgn n (_node_map state)
                , _node_map_rev = Map.insert n lgn (_node_map_rev state)
                }
            )
    in \lgn -> MTL.gets ((lgn `Map.lookup`) . _node_map) >>= \case
  Just n  -> return n
  Nothing -> do
        n <- getUnusedNode
        insertLNode (n, lgn)
        return n
addNodes :: Vector LicenseGraphNode -> LicenseGraphM (Vector G.Node)
addNodes = V.mapM addNode

addEdge :: (LicenseGraphNode, LicenseGraphNode, LicenseGraphEdge) -> LicenseGraphM G.Node
addEdge = let
        addEdge' :: G.LEdge LicenseGraphEdge -> LicenseGraphM ()
        addEdge' edge = do
            alreadyHasTheEdge <- MTL.gets ((`G.hasLEdge` edge) . _gr)
            unless alreadyHasTheEdge $
                MTL.modify (\state -> state { _gr = edge `G.insEdge` _gr state })
    in \(a,b,e) -> do
        na <- addNode a
        nb <- addNode b
        unless (na == nb) $ do
            addEdge' (na, nb, e)
            when (e == Same) $
                addEdge' (nb, na, e)
        return na
addEdges :: Vector (LicenseGraphNode, LicenseGraphNode, LicenseGraphEdge) -> LicenseGraphM (Vector G.Node)
addEdges = V.mapM addEdge

-- ############################################################################

stderrLog :: String -> LicenseGraphM ()
stderrLog msg = MTL.liftIO $ hPutStrLn stderr (color Green msg)

-}