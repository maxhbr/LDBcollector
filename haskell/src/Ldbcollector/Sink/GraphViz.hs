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

computeDigraph :: LicenseGraphType -> GV.DotGraph G.Node
computeDigraph graph = let
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
                                Just (Vec v) -> GV.toLabelValue ((unlines . map show) v)
                                Just (LGValue _) -> GV.toLabelValue "$VALUE"
                                Just (Rule _) -> GV.toLabelValue "$Rule"
                                Just nodeLabel' -> GV.toLabelValue (show nodeLabel')
                                Nothing -> GV.toLabelValue "(/)"
                    styling = case nodeLabel of
                        Just (LGValue _) -> [ GV.FillColor [GV.WC (GV.X11Color GV.Beige) (Just 1)]
                                            , GV.FontColor (GV.X11Color GV.Gray)
                                            -- , GV.Shape GV.PlainText
                                            ]
                        Just (Rule _) -> [ GV.FillColor [GV.WC (GV.X11Color GV.Beige) (Just 1)]
                                         , GV.FontColor (GV.X11Color GV.Gray)
                                         -- , GV.Shape GV.PlainText
                                         ]
                        _ -> []
                in  GV.Label label : styling
            , GV.fmtEdge          = \(a, b, _) ->
                (case nub (edgeLabels a b) of
                    [] -> []
                    [Same] -> []
                    edgeLabels' -> (case edgeLabels' of
                        [Potentially _] -> [GV.style GV.dashed]
                        _ -> []) ++ [ GV.Label (GV.toLabelValue . unlines . map show $ edgeLabels') ]
                )
            }
    in GV.graphToDot params graph

getDigraph :: LicenseGraphM (GV.DotGraph G.Node)
getDigraph = MTL.gets (computeDigraph . _gr)

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
