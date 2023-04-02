{-# LANGUAGE GADTs             #-}
{-# LANGUAGE LambdaCase        #-}
{-# LANGUAGE OverloadedStrings #-}
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

import qualified Control.Monad.State                 as MTL
import           Data.Aeson                          as A
import           Data.Aeson.Encode.Pretty            as A
import qualified Data.ByteString.Char8               as B (unpack)
import qualified Data.ByteString.Lazy                as BL (toStrict)
import qualified Data.Graph.Inductive.Graph          as G
import qualified Data.Graph.Inductive.PatriciaTree   as G
import qualified Data.Map                            as Map
import qualified Data.Set                            as Set
import qualified Data.Vector                         as V
import           System.Console.Pretty               (Color (Green), color)

import qualified Control.Monad.Reader                as MTL
import           Ldbcollector.Model.LicenseFact
import           Ldbcollector.Model.LicenseName
import           Ldbcollector.Model.LicenseStatement

-- ############################################################################

stderrLog :: String -> LicenseGraphM ()
stderrLog msg = MTL.liftIO $ hPutStrLn stderr (color Green msg)

-- ############################################################################

data LicenseGraphNode where
    LGName      :: LicenseName -> LicenseGraphNode
    LGStatement :: LicenseStatement -> LicenseGraphNode
    LGLicenseText :: Text -> LicenseGraphNode
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
        fun _           = []
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
                        Just (LGFact _) -> True
                        Just (LGStatement _) -> True
                        _               -> False
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
            when (e == LGNameRelation Same) $
                insertLEdge (nb, na, e)
        return na
insertEdges :: Vector (LicenseGraphNode, LicenseGraphNode, LicenseGraphEdge) -> WithFactM (Vector G.Node)
insertEdges = V.mapM insertEdge

applyFact :: WithFactM G.Node
applyFact = do
    fact <- MTL.asks snd
    let factLG = LGFact fact
    factNode <- insertNode (LGFact fact)
    lnNode <- applyFactApplicableLNs (getApplicableLNs fact)
    insertEdge (factLG, lnNode, LGAppliesTo)
    stmtNodes <- applyFactImpliedStmts (getImpliedStmts fact)
    let edges = V.fromList $ map (,factLG, LGImpliedBy) stmtNodes
    insertEdges edges
    return factNode

applyFactApplicableLNs :: ApplicableLNs -> WithFactM LicenseGraphNode
applyFactApplicableLNs (LN ln) = let
      node = LGName ln
    in insertNode node >> return node
applyFactApplicableLNs (NLN ln) = let
      namespacelessLN = unsetNS ln
    in applyFactApplicableLNs $ if ln == namespacelessLN
                                then LN ln
                                else LN ln `AlternativeLNs` [LN namespacelessLN]
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

applyFactImpliedStmts :: [ImpliedStmt] -> WithFactM [LicenseGraphNode]
applyFactImpliedStmts stmts = mconcat <$> mapM applyFactImpliedStmt stmts

applyFactImpliedStmt :: ImpliedStmt -> WithFactM [LicenseGraphNode]
applyFactImpliedStmt (Stmt stmt) = do
    let stmtLG = LGStatement stmt
    _ <- insertNode stmtLG
    return [stmtLG]
applyFactImpliedStmt (MStmt (Just stmt)) = applyFactImpliedStmt (Stmt stmt)
applyFactImpliedStmt (MStmt Nothing)     = pure []
applyFactImpliedStmt (stmt `StmtRel` stmt') = do
    nodes <- applyFactImpliedStmt stmt
    nodes' <- applyFactImpliedStmt stmt'
    let edges = V.fromList $ concatMap (\node -> map (, node, LGImpliedBy) nodes') nodes
    insertEdges edges
    return nodes
applyFactImpliedStmt (LicenseText text) = do
    let textLG = LGLicenseText text
    _ <- insertNode textLG
    return [textLG]
