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
import qualified Data.HashMap.Internal.Strict      as HMap
import qualified Data.Map                          as Map
import qualified Data.GraphViz.Attributes.HTML     as GVH

import qualified Text.Wrap                         as TW

computeDigraph :: LicenseGraph -> GV.DotGraph G.Node
computeDigraph (LicenseGraph {_gr = graph, _facts = facts}) = let
        colors = cycle $ map (\(r,g,b) -> GV.RGB r g b) [ (0,135,108)  -- #00876c 
                                                        , (55,148,105) -- #379469 
                                                        , (88,160,102) -- #58a066 
                                                        , (120,171,99) -- #78ab63 
                                                        , (152,181,97) -- #98b561 
                                                        , (184,191,98) -- #b8bf62 
                                                        , (218,199,103)-- #dac767 
                                                        , (222,178,86) -- #deb256 
                                                        , (224,157,75) -- #e09d4b 
                                                        , (225,135,69) -- #e18745 
                                                        , (224,111,69) -- #e06f45 
                                                        , (220,87,74)  -- #dc574a 
                                                        , (212,61,81)  -- #d43d51 
                                                        ]
                                                        -- [ (255,215,0)
                                                        -- , (255,177,78)
                                                        -- , (250,135,117)
                                                        -- , (234,95,148)
                                                        -- , (205,52,181)
                                                        -- , (157,2,215)
                                                        -- , (0,0,255)
                                                        -- ]
        origins = (map fst . Map.keys) facts
        factColoringMap = Map.fromList $ zip origins colors
        typeColoringLookup origin = Map.findWithDefault (GV.RGB 0 0 0) origin factColoringMap

        getOriginsOfNode :: G.Node -> [Origin]
        getOriginsOfNode n = ( nub
                             . sort
                             . mapMaybe (\((origin, _), (nodes,_)) ->
                                  if n `elem` nodes
                                  then Just origin
                                  else Nothing)
                             . Map.assocs
                             ) facts

        getColorOfNode :: (G.Node, Maybe LicenseGraphNode) -> GV.Attributes
        getColorOfNode (n, Just (LGName _)) =
            case getOriginsOfNode n of 
                [origin] -> [ (GV.Color . (:[]) . (`GV.WC` Nothing) . typeColoringLookup) origin ]
                [] -> [GV.Style [GV.SItem GV.Dashed []]]
                _ -> []
        getColorOfNode (n, Just (LGFact _)) = 
            case getOriginsOfNode n of 
                [origin] -> [ GV.FontColor (GV.X11Color GV.Gray)
                            , (GV.Color . (:[]) . (`GV.WC` Nothing) . typeColoringLookup) origin 
                            ]
                [] -> [GV.Style [GV.SItem GV.Dashed []]]
                _ -> []
        getColorOfNode _ = []

        getOriginsOfEdge :: G.Edge -> [Origin]
        getOriginsOfEdge n = ( nub
                             . sort
                             . mapMaybe (\((origin, _), (_,edges)) ->
                                  if n `elem` edges
                                  then Just origin
                                  else Nothing)
                             . Map.assocs
                             ) facts

        getColorOfEdge :: G.LEdge LicenseGraphEdge -> GV.Attributes
        getColorOfEdge edge = let
                potentialE = (fmap G.toEdge . find (== edge) . G.labEdges) graph
            in case potentialE of
                Just e -> case getOriginsOfEdge e of 
                        [origin] -> [ (GV.Color . (:[]) . (`GV.WC` Nothing) . typeColoringLookup) origin ]
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
                                Just (LGStatement (LicenseComment r)) -> GV.toLabelValue (TW.wrapText TW.defaultWrapSettings 80 r)
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
                        [LGNameRelation Same] -> [GV.style GV.bold]
                        _ -> []) ++ [ GV.Label (GV.toLabelValue . unlines . map show $ edgeLabels') ]
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
