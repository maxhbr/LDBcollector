{-# LANGUAGE LambdaCase #-}
module Ldbcollector.Sink.GraphViz
    ( writeGraphViz
    ) where

import qualified Control.Exception                 as Ex
import qualified Control.Monad.State               as MTL
import qualified Data.Graph.Inductive.Graph        as G
import qualified Data.Graph.Inductive.Monad        as G
import qualified Data.Graph.Inductive.PatriciaTree as G
import qualified Data.Graph.Inductive.Query.DFS    as G
import qualified Data.GraphViz                     as GV
import qualified Data.GraphViz.Attributes.Complete as GV
import qualified Data.GraphViz.Commands.IO         as GV
import qualified Data.GraphViz.Printing            as GV
import qualified Data.Vector                       as V

import           Ldbcollector.Model
import qualified Data.HashMap.Internal.Strict as HMap
import qualified Data.Map                     as Map
import qualified Data.GraphViz.Attributes.HTML as GVH

computeDigraph :: LicenseGraph -> GV.DotGraph G.Node
computeDigraph (LicenseGraph {_gr = graph, _facts = facts}) = let
        colors = cycle $ map (\(r,g,b) -> GV.RGB r g b) [ (255,215,0)
                                                        , (255,177,78)
                                                        , (250,135,117)
                                                        , (234,95,148)
                                                        , (205,52,181)
                                                        , (157,2,215)
                                                        , (0,0,255)
                                                        ]
        origins = (map fst . Map.keys) facts
        factTypes = ( nub
                    . sort
                    . map getType
                    . mapMaybe (\case
                        (_,LGFact fact) -> Just fact
                        _ -> Nothing)
                    . G.labNodes
                    ) graph
        factColoringMap = Map.fromList $ zip factTypes colors
        typeColoringLookup factType = Map.findWithDefault (GV.RGB 0 0 0) factType factColoringMap
        factColoringLookup = typeColoringLookup . getType

        getColorOfNode :: (G.Node, Maybe LicenseGraphNode) -> GV.Attributes
        getColorOfNode (n, Just (LGName _)) = let
               types = ( nub
                       . sort
                       . map getType
                       . mapMaybe (\((_,fact), (nodes,_)) ->
                            if n `elem` nodes
                            then Just fact
                            else Nothing)
                       . Map.assocs
                       ) facts
            in case types of 
                [factType] -> [ (GV.Color . (:[]) . (`GV.WC` Nothing) . typeColoringLookup) factType ]
                [] -> [GV.Style [GV.SItem GV.Dashed []]]
                _ -> []
        getColorOfNode (_, Just (LGFact fact)) = [ GV.FontColor (GV.X11Color GV.Gray)
                                                 , (GV.Color . (:[]) . (`GV.WC` Nothing) . factColoringLookup) fact
                                                 ]
        getColorOfNode _ = []

        getColorOfEdge :: G.LEdge LicenseGraphEdge -> GV.Attributes
        getColorOfEdge edge = let
                potentialE = (fmap G.toEdge . find (== edge) . G.labEdges) graph
            in case potentialE of
                Just e -> let
                        types = ( nub
                                . sort
                                . map getType
                                . mapMaybe (\((_,fact), (_, edges)) ->
                                    if e `elem` edges
                                    then Just fact
                                    else Nothing)
                                . Map.assocs
                                ) facts
                    in case types of 
                        [factType] -> [ (GV.Color . (:[]) . (`GV.WC` Nothing) . typeColoringLookup) factType ]
                        [] -> []
                        _ -> []
                Nothing -> []
        
        edgeLabels a b =
            ( map (\(_, _, l) -> l)
            . filter (\(a', b', _) -> a == a' && b == b')
            . G.labEdges
            )
            graph
        params = GV.nonClusteredParams
            { GV.isDirected       = True
            , GV.globalAttributes = [ GV.NodeAttrs [GV.Shape GV.BoxShape]
                                    , GV.GraphAttrs [GV.Splines GV.Curved]
                                    ]
            , GV.fmtNode          = \(n, l) ->
                let nodeLabel = graph `G.lab` n
                    label = case nodeLabel of
                                Just (LGName name) -> GV.toLabelValue (show name)
                                Just (LGStatement (LicenseUrl url)) -> GV.toLabelValue url
                                Just (LGStatement (LicenseRule r)) -> GV.toLabelValue "$RULE"
                                Just (LGStatement (LicenseText r)) -> GV.toLabelValue "$TEXT"
                                Just (LGStatement (LicenseComment r)) -> GV.toLabelValue "$COMMENT"
                                Just (LGStatement stmt) -> GV.toLabelValue stmt
                                Just (LGFact fact) -> GV.toLabelValue (getFactId fact)
                                -- Just nodeLabel' -> GV.toLabelValue (show nodeLabel')
                                Nothing -> GV.toLabelValue "(/)"
                                _ -> GV.toLabelValue "(?)"
                    coloring = getColorOfNode (n,nodeLabel)
                    styling = case nodeLabel of
                        Just (LGStatement _) -> [ GV.FillColor [GV.WC (GV.X11Color GV.Beige) (Just 1)]
                                                , GV.Shape GV.PlainText
                                                ]
                        Just (LGFact _) -> [ GV.FillColor [GV.WC (GV.X11Color GV.Beige) (Just 1)]
                                                , GV.Shape GV.Ellipse
                                                ]
                        _ -> []
                in  GV.Label label : (coloring ++ styling)
            , GV.fmtEdge          = \(a, b, e) ->
                (case nub (edgeLabels a b) of
                    [] -> []
                    [LGNameRelation Same] -> []
                    [LGNameRelation Better] -> [GV.style GV.dashed]
                    [LGAppliesTo] -> []
                    [LGImpliedBy] -> []
                    edgeLabels' -> (case edgeLabels' of
                        [LGNameRelation (Potentially _)] -> [GV.style GV.dashed]
                        _                                -> []) ++ [ GV.Label (GV.toLabelValue . unlines . map show $ edgeLabels') ]
                ) ++ getColorOfEdge (a, b, e)
            }
    in GV.graphToDot params graph

getDigraph :: LicenseGraphM (GV.DotGraph G.Node)
getDigraph = MTL.gets computeDigraph

writeGraphViz :: FilePath -> LicenseGraphM ()
writeGraphViz dot = do
    stderrLog $ "generate " ++ dot

    digraph <- getDigraph
    let format = GV.Svg
    let command = GV.Fdp
    res <- MTL.liftIO $ do
        createParentDirectoryIfNotExists dot
        writeFile
            (dot <.> "graph")
            (G.prettify (GV.dotToGraph digraph :: G.Gr GV.Attributes GV.Attributes))
        GV.writeDotFile dot digraph
        Ex.try $ GV.runGraphvizCommand command digraph format (dot <.> show format)
    case res of
        Left (Ex.SomeException e) -> stderrLog $ "failed to convert dot to "++ show format ++ ": " ++ show e
        Right svg -> stderrLog $ "wrote SVG " ++ svg
