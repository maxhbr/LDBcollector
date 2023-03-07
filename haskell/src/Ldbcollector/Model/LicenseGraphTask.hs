module Ldbcollector.Model.LicenseGraphTask
    ( LicenseGraphTask (..)
    , maybeToTask, ifToTask
    , applyTask
    , fromValue
    ) where

import           MyPrelude

import qualified Data.Vector                     as V

import           Control.Monad                   (liftM2)
import           Ldbcollector.Model.LicenseGraph
import           Ldbcollector.Model.LicenseName

data LicenseGraphTask where
    Noop :: LicenseGraphTask
    Add :: LicenseGraphNode -> LicenseGraphTask
    Adds :: Vector LicenseGraphNode -> LicenseGraphTask
    AddTs :: Vector LicenseGraphTask -> LicenseGraphTask
    Edge :: LicenseGraphTask -> LicenseGraphEdge -> LicenseGraphTask -> LicenseGraphTask
    EdgeLeft :: LicenseGraphTask -> LicenseGraphEdge -> LicenseGraphTask -> LicenseGraphTask
    EdgeUnion :: LicenseGraphTask -> LicenseGraphEdge -> LicenseGraphTask -> LicenseGraphTask
    Pure :: LicenseGraphM () -> LicenseGraphTask
instance IsString LicenseGraphTask where
    fromString = Add . fromString

fromValue :: ToJSON a => a -> (a -> LicenseGraphNode) -> (a -> Maybe LicenseGraphNode) -> LicenseGraphTask
fromValue a getId getBetterId = let
        valueT = Add $ mkLGValue a
        idT = let
              idT' = Add $ getId a
          in case getBetterId a of
            Just betterId -> Edge idT' Better (Add betterId)
            Nothing       -> idT'
    in Edge valueT AppliesTo idT

maybeToTask :: (a -> LicenseGraphTask) -> Maybe a -> LicenseGraphTask
maybeToTask _ Nothing  = Noop
maybeToTask f (Just a) = f a
ifToTask :: LicenseGraphNode -> Bool -> LicenseGraphTask
ifToTask _ False = Noop
ifToTask n True  = Add n

applyEdgeTask :: LicenseGraphTask -> LicenseGraphEdge -> LicenseGraphTask -> LicenseGraphM (Vector LicenseGraphNode, Vector LicenseGraphNode)
applyEdgeTask left edge right = do
    leftNodes <- applyTask' left
    rightNodes <- applyTask' right
    let pairs = liftM2 (,) leftNodes rightNodes
    let edges = V.map (\(leftNode,rightNode) -> (leftNode,rightNode,edge)) pairs
    addEdges edges
    return (leftNodes, rightNodes)

applyTask' :: LicenseGraphTask -> LicenseGraphM (Vector LicenseGraphNode)
applyTask' Noop = pure V.empty
applyTask' (Add node) = do
    addNode node
    return (V.singleton node)
applyTask' (Adds nodes) = do
    addNodes nodes
    return nodes
applyTask' (Edge left edge right) = do
    (leftNodes, _) <- applyEdgeTask left edge right
    return leftNodes
applyTask' (EdgeLeft left edge right) = do
    (_, rightNodes) <- applyEdgeTask left edge right
    return rightNodes
applyTask' (EdgeUnion left edge right) = do
    (leftNodes, rightNodes) <- applyEdgeTask left edge right
    return (leftNodes <> rightNodes)
applyTask' (AddTs tasks) = do
    nodes <- V.mapM applyTask' tasks
    return (join nodes)
applyTask' (Pure m) = do
    m
    return V.empty

applyTask :: LicenseGraphTask -> LicenseGraphM ()
applyTask = void . applyTask'
