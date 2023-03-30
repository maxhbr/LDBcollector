{-# OPTIONS_GHC -Wno-unrecognised-pragmas #-}
{-# HLINT ignore "Use tuple-section" #-}
module Ldbcollector.Model.LicenseGraphTask
    where
    {-
    ( LicenseGraphTask (..)
    , maybeToTask, ifToTask
    , applyTask
    -- , fromValue
    ) where
    -}

-- import           MyPrelude

-- import qualified Data.Vector                     as V
-- import           Data.Aeson                        as A

-- import           Ldbcollector.Model.LicenseName
-- import           Ldbcollector.Model.LicenseGraph


-- data LicenseGraphTask where
--     Noop :: LicenseGraphTask

--     AddLN :: LicenseName -> LicenseGraphTask
--     SameLNs :: [LicenseName] -> LicenseGraphTask -> LicenseGraphTask
--     -- BetterLNs :: [LicenseName] -> LicenseGraphTask -> LicenseGraphTask

--     -- ValueApplies :: [LicenseGraphNode] -> A.Value -> LicenseName -> LicenseGraphTask

--     Pure :: WithFactM () -> LicenseGraphTask


-- maybeToTask :: (a -> LicenseGraphTask) -> Maybe a -> LicenseGraphTask
-- maybeToTask _ Nothing  = Noop
-- maybeToTask f (Just a) = f a





-- applyEdgeTask :: LicenseGraphTask -> LicenseGraphEdge -> LicenseGraphTask -> WithFactM (Vector LicenseGraphNode, Vector LicenseGraphNode)
-- applyEdgeTask left edge right = do
--     leftNodes <- applyTask' left
--     rightNodes <- applyTask' right
--     let pairs = liftM2 (,) leftNodes rightNodes
--     let edges = V.map (\(leftNode,rightNode) -> (leftNode,rightNode,edge)) pairs
--     _ <- insertEdges edges
--     return (leftNodes, rightNodes)

-- applyTask' :: LicenseGraphTask -> WithFactM (Vector LicenseGraphNode)
-- applyTask' Noop = pure mempty
-- applyTask' (AddLN ln) = let
--       node = LGName ln
--     in insertNode node >> return (V.singleton node)
-- applyTask' (SameLNs sames t) = do
--     tNodes <- applyTask' t
--     sNodes <- mconcat <$> mapM (applyTask' . AddLN) sames
--     let edges = V.concatMap (\tNode -> V.map (,tNode, LGNameRelation Same) sNodes) tNodes
--     _ <- insertEdges edges
--     return sNodes
-- applyTask' (Pure p) = p >> return mempty












-- -- applyTask' (BetterLNs betters t) = pure V.empty
-- -- applyTask' (ValueApplies statements value ln) = pure V.empty
-- -- applyTask' (Add node) = do
-- --     _ <- addNode node
-- --     return (V.singleton node)
-- -- applyTask' (Adds nodes) = do
-- --     _ <- addNodes nodes
-- --     return nodes
-- -- applyTask' (Edge left edge right) = do
-- --     (leftNodes, _) <- applyEdgeTask left edge right
-- --     return leftNodes
-- -- applyTask' (EdgeLeft left edge right) = do
-- --     (_, rightNodes) <- applyEdgeTask left edge right
-- --     return rightNodes
-- -- applyTask' (EdgeUnion left edge right) = do
-- --     (leftNodes, rightNodes) <- applyEdgeTask left edge right
-- --     return (leftNodes <> rightNodes)
-- -- applyTask' (AddTs tasks) = do
-- --     nodes <- V.mapM applyTask' tasks
-- --     return (join nodes)
-- -- applyTask' (Pure m) = do
-- --     m
-- --     return V.empty

-- -- applyTask :: (Origin, LicenseFact) -> LicenseGraphTask -> LicenseFactM ()
-- -- applyTask = void . applyTask'


-- {-
--     Add :: LicenseGraphNode -> LicenseGraphTask
--     Adds :: Vector LicenseGraphNode -> LicenseGraphTask
--     AddTs :: Vector LicenseGraphTask -> LicenseGraphTask
--     Edge :: LicenseGraphTask -> LicenseGraphEdge -> LicenseGraphTask -> LicenseGraphTask
--     EdgeLeft :: LicenseGraphTask -> LicenseGraphEdge -> LicenseGraphTask -> LicenseGraphTask
--     EdgeUnion :: LicenseGraphTask -> LicenseGraphEdge -> LicenseGraphTask -> LicenseGraphTask
-- instance IsString LicenseGraphTask where
--     fromString = Add . fromString

-- -- fromValue :: (Typeable a, ToJSON a) => a -> (a -> LicenseGraphNode) -> (a -> Maybe LicenseGraphNode) -> LicenseGraphTask
-- -- fromValue a getId getBetterId = let
-- --         valueT = Add $ mkLGValue a
-- --         idT = let
-- --               idT' = Add $ getId a
-- --           in case getBetterId a of
-- --             Just betterId -> Edge idT' Better (Add betterId)
-- --             Nothing       -> idT'
-- --     in Edge valueT AppliesTo idT

-- applyEdgeTask :: LicenseGraphTask -> LicenseGraphEdge -> LicenseGraphTask -> LicenseFactM (Vector LicenseGraphNode, Vector LicenseGraphNode)
-- applyEdgeTask left edge right = do
--     leftNodes <- applyTask' left
--     rightNodes <- applyTask' right
--     let pairs = liftM2 (,) leftNodes rightNodes
--     let edges = V.map (\(leftNode,rightNode) -> (leftNode,rightNode,edge)) pairs
--     _ <- addEdges edges
--     return (leftNodes, rightNodes)

-- applyTask' :: LicenseGraphTask -> LicenseFactM (Vector LicenseGraphNode)
-- applyTask' Noop = pure V.empty
-- -- applyTask' (AddLN ln) = let
-- --       node = LicenseName ln
-- --     in addNode node >> return (V.singleton node)
-- -- applyTask' (SameLNs sames t) = let
-- --     in do
-- --         right <
-- -- applyTask' (BetterLNs betters t) = pure V.empty
-- -- applyTask' (ValueApplies statements value ln) = pure V.empty
-- applyTask' (Add node) = do
--     _ <- addNode node
--     return (V.singleton node)
-- applyTask' (Adds nodes) = do
--     _ <- addNodes nodes
--     return nodes
-- applyTask' (Edge left edge right) = do
--     (leftNodes, _) <- applyEdgeTask left edge right
--     return leftNodes
-- applyTask' (EdgeLeft left edge right) = do
--     (_, rightNodes) <- applyEdgeTask left edge right
--     return rightNodes
-- applyTask' (EdgeUnion left edge right) = do
--     (leftNodes, rightNodes) <- applyEdgeTask left edge right
--     return (leftNodes <> rightNodes)
-- applyTask' (AddTs tasks) = do
--     nodes <- V.mapM applyTask' tasks
--     return (join nodes)
-- applyTask' (Pure m) = do
--     m
--     return V.empty

-- applyTask :: LicenseGraphTask -> LicenseFactM ()
-- applyTask = void . applyTask'

-- -}