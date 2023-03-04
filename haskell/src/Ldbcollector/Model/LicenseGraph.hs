{-# LANGUAGE LambdaCase #-}
module Ldbcollector.Model.LicenseGraph
  ( LicenseGraphNode (..)
  , mkLGValue
  , LicenseGraphEdge (..)
  , LicenseGraph (_gr, _node_map, _node_map_rev), LicenseGraphType
  , LicenseGraphM
  , runLicenseGraphM
  , addNode, addNodes
  , addEdge, addEdges
  , focus
  , getFocused
  , stderrLog
  ) where

import           MyPrelude

import qualified Control.Monad.State               as MTL
import           Data.Aeson                        as A
import           Data.Aeson.Encode.Pretty          as A
import qualified Data.ByteString.Char8             as B (unpack)
import qualified Data.ByteString.Lazy              as BL (toStrict)
import qualified Data.Graph.Inductive.Basic        as G
import qualified Data.Graph.Inductive.Graph        as G
import qualified Data.Graph.Inductive.Monad        as G
import qualified Data.Graph.Inductive.PatriciaTree as G
import qualified Data.Graph.Inductive.Query.DFS    as G
import qualified Data.Map                          as Map
import           Data.String                       (IsString (..))
import qualified Data.Vector                       as V
import           System.Console.Pretty             (Color (Green), color)
import qualified System.FilePath                   as FP
import           System.IO                         (hPutStrLn, stderr)


import           Ldbcollector.Model.LicenseName

data LicenseGraphNode where
    LicenseName :: LicenseName -> LicenseGraphNode
    Data :: Text -> LicenseGraphNode
    LGValue :: A.Value -> LicenseGraphNode
    Vec :: [LicenseGraphNode] -> LicenseGraphNode
    deriving (Eq, Ord)
instance Show LicenseGraphNode where
    show (LicenseName ln) = show ln
    show (Data d)         = show d
    show (LGValue v)      = B.unpack . BL.toStrict $ A.encodePretty v
    show (Vec v)          = show v
mkLGValue :: ToJSON a => a -> LicenseGraphNode
mkLGValue = LGValue . toJSON
instance IsString LicenseGraphNode where
    fromString s = Data (pack s)
data LicenseGraphEdge where
    Same      :: LicenseGraphEdge
    Better    :: LicenseGraphEdge
    AppliesTo :: LicenseGraphEdge
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
addEdge (a,b,e) = do
    na <- addNode a
    nb <- addNode b
    unless (na == nb) $ do
        MTL.modify
            (\state -> state { _gr = (na, nb, e) `G.insEdge` _gr state })
        when (e == Same) $
            MTL.modify
                (\state -> state { _gr = (nb, na, e) `G.insEdge` _gr state })
    return na
addEdges :: Vector (LicenseGraphNode, LicenseGraphNode, LicenseGraphEdge) -> LicenseGraphM (Vector G.Node)
addEdges = V.mapM addEdge

-- ############################################################################

focus' :: Vector G.Node -> LicenseGraph -> LicenseGraph
focus' needles (LicenseGraph gr node_map node_map_rev) = let

        reachableForNeedle needle = G.reachable needle gr ++ G.reachable needle (G.grev gr)
        allReachable = concatMap reachableForNeedle (V.toList needles)
        isReachable n = n `elem` allReachable
    in LicenseGraph {
        _gr = G.nfilter isReachable gr,
        _node_map = Map.filter isReachable node_map,
        _node_map_rev = Map.filterWithKey(\k a -> isReachable k) node_map_rev
    }

focus :: Vector LicenseGraphNode -> LicenseGraphM a -> LicenseGraphM a
focus needles inner = do
    stderrLog "get graph"
    frozen <- MTL.get
    (a,_) <- (MTL.lift . runLicenseGraphM' frozen) $ do
        stderrLog "focus graph"
        needleIds <- addNodes needles
        state <- MTL.modify (focus' needleIds)
        stderrLog "work on focused graph"
        inner
    stderrLog "end focusing"
    return a

getFocused :: Vector LicenseGraphNode -> LicenseGraphM LicenseGraph
getFocused needles = focus needles MTL.get

-- ############################################################################

stderrLog :: String -> LicenseGraphM ()
stderrLog msg = MTL.liftIO $ hPutStrLn stderr (color Green msg)
