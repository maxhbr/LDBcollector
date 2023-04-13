{-# LANGUAGE LambdaCase        #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE CPP               #-}
module Ldbcollector.Sink.GraphViz
    ( writeGraphViz
    , genGraphViz
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

import qualified Data.GraphViz.Attributes.HTML     as GVH
import qualified Data.GraphViz.Attributes.Colors.SVG as GVH
import qualified Data.HashMap.Internal.Strict      as HMap
import qualified Data.Map                          as Map
import           Ldbcollector.Model

import qualified Data.Text.Lazy                    as LT
import qualified Data.Text.Lazy.IO                 as LT
import qualified System.IO.Temp                    as Temp
import qualified Text.Wrap                         as TW
import qualified Data.GraphViz.Attributes.Colors as GVH

factIdToLabelValue :: FactId -> GV.Label
factIdToLabelValue (FactId ty hash) = GV.toLabelValue (ty ++ "\n" ++ hash)

licenseStatementToLabelValue :: LicenseStatement -> GV.Label
licenseStatementToLabelValue (LicenseStatement stmt) = GV.toLabelValue stmt
licenseStatementToLabelValue (LicenseUrl url) = GV.toLabelValue url
licenseStatementToLabelValue (LicenseText txt) = GV.toLabelValue ("$TEXT" :: Text)
licenseStatementToLabelValue (LicenseRule txt) = GV.toLabelValue ("$RULE" :: Text)
licenseStatementToLabelValue (LicenseComment txt) = GV.toLabelValue (TW.wrapText TW.defaultWrapSettings 80 txt)
licenseStatementToLabelValue (LicensePCLR pclr) = let
            header = GVH.Cells [ GVH.LabelCell [] (GVH.Text [GVH.Str "Permissions"])
                               , GVH.LabelCell [] (GVH.Text [GVH.Str "Conditions"])
                               , GVH.LabelCell [] (GVH.Text [GVH.Str "Limitations"])
                               , GVH.LabelCell [] (GVH.Text [GVH.Str "Restrictions"])
                               ]
            linesToContent :: [Text] -> GVH.Cell
            linesToContent = GVH.LabelCell [] . GVH.Text . intersperse newline . map (GVH.Str . LT.fromStrict)
            newline = GVH.Newline []
            content = GVH.Cells (map linesToContent [ _permissions pclr, _conditions pclr, _limitations pclr, _restrictions pclr])
        in GV.HtmlLabel . GVH.Table $ GVH.HTable Nothing [] [ header, content ]
#if 0
licenseStatementToLabelValue (LicenseCompatibilities compatibilities) = let
            mkLine (LicenseCompatibility other compatibility explanation) =
                GVH.Cells [ GVH.LabelCell [] (GVH.Text [GVH.Str . LT.pack $ show other])
                          , GVH.LabelCell [] (GVH.Text [GVH.Str $ LT.pack compatibility])
                        --   , GVH.LabelCell [] (GVH.Text [GVH.Str $ LT.fromStrict explanation])
                          ]
        in GV.HtmlLabel . GVH.Table $ GVH.HTable Nothing [] (map mkLine compatibilities)
#else
licenseStatementToLabelValue (LicenseCompatibilities compatibilities) = GV.toLabelValue ("$COMPATIBILITIES" :: Text)
#fi
licenseStatementToLabelValue (LicenseRating ns rating) = let
           color = GVH.Color . GVH.SVGColor $ case rating of
            NegativeLicenseRating _ _ -> GVH.DarkRed
            NeutralLicenseRating _ _ -> GVH.Black
            PositiveLicenseRating _ _ -> GVH.ForestGreen
        in GV.HtmlLabel . GVH.Text $ [GVH.Str (fromString ns), GVH.Str ": ", GVH.Format GVH.Bold [GVH.Font [color] [(GVH.Str . LT.fromStrict . unLicenseRating) rating]]]
licenseStatementToLabelValue statement = (GV.StrLabel . LT.pack . show) statement

simplifyEdgeLabel :: [LicenseGraphEdge] -> [LicenseGraphEdge]
simplifyEdgeLabel [] = []
simplifyEdgeLabel [a] = [a]
simplifyEdgeLabel as = let
        getAllLnRelations [] = Just []
        getAllLnRelations (LGNameRelation r:as) = fmap (r :) (getAllLnRelations as)
        getAllLnRelations _ = Nothing
    in case getAllLnRelations as of
        Just lns -> if Same `elem` lns
                    then [LGNameRelation Same]
                    else if Better `elem` lns
                         then [LGNameRelation Better]
                         else as
        _ -> nub as

generateColorMapping :: Ord a => [a] -> Map.Map a GV.Color
generateColorMapping = let
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
    in Map.fromList . (`zip` colors)

computeDigraph :: LicenseGraph -> [G.Node] -> [G.Node] -> [G.Node] -> GV.DotGraph G.Node
computeDigraph (LicenseGraph {_gr = graph, _facts = facts}) mainLNs sameLNs otherLNs = let
        factColoringMap = generateColorMapping ((map fst . Map.keys) facts)
        typeColoringLookup source = Map.findWithDefault (GV.RGB 0 0 0) source factColoringMap

        getSourcesOfNode :: G.Node -> [SourceRef]
        getSourcesOfNode n = ( nub
                             . sort
                             . mapMaybe (\((source, _), (nodes,_)) ->
                                  if n `elem` nodes
                                  then Just source
                                  else Nothing)
                             . Map.assocs
                             ) facts

        getColorOfNode :: (G.Node, Maybe LicenseGraphNode) -> GV.Attributes
        getColorOfNode (n, Just (LGName _)) =
            case getSourcesOfNode n of
                [source] -> [ (GV.Color . (:[]) . (`GV.WC` Nothing) . typeColoringLookup) source ]
                [] -> [GV.Style [GV.SItem GV.Dashed []]]
                _ -> []
        getColorOfNode (n, Just (LGFact _)) =
            case getSourcesOfNode n of
                [source] -> [ GV.FontColor (GV.X11Color GV.Gray)
                            , (GV.Color . (:[]) . (`GV.WC` Nothing) . typeColoringLookup) source
                            ]
                [] -> [GV.Style [GV.SItem GV.Dashed []]]
                _ -> []
        getColorOfNode _ = []

        getSourcesOfEdge :: G.Edge -> [SourceRef]
        getSourcesOfEdge n = ( nub
                             . sort
                             . mapMaybe (\((source, _), (_,edges)) ->
                                  if n `elem` edges
                                  then Just source
                                  else Nothing)
                             . Map.assocs
                             ) facts

        getColorOfEdge :: G.LEdge LicenseGraphEdge -> GV.Attributes
        getColorOfEdge edge = let
                potentialE = (fmap G.toEdge . find (== edge) . G.labEdges) graph
            in case potentialE of
                Just e -> case getSourcesOfEdge e of
                        [source] -> [ (GV.Color . (:[]) . (`GV.WC` Nothing) . typeColoringLookup) source ]
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
                                Just (LGStatement stmt) -> licenseStatementToLabelValue stmt
                                Just (LGFact fact) -> factIdToLabelValue (getFactId fact)
                                Just nodeLabel' -> GV.toLabelValue (show nodeLabel')
                                Nothing -> GV.toLabelValue ("(/)" :: Text)
                    coloring = getColorOfNode (n,nodeLabel)
                    styling = case nodeLabel of
                        Just (LGStatement _) -> [ GV.FillColor [GV.WC (GV.X11Color GV.Beige) (Just 1)]
                                                , GV.Shape GV.PlainText
                                                ]
                        Just (LGFact _) -> [ GV.FillColor [GV.WC (GV.X11Color GV.Beige) (Just 1)]
                                                , GV.Shape GV.Ellipse
                                                ]
                        Just (LGName _) -> if n `elem` mainLNs
                                           then [GV.Shape GV.TripleOctagon]
                                           else if n `elem` sameLNs 
                                                then [GV.Shape GV.DoubleOctagon]
                                                else if n `elem` otherLNs
                                                     then [GV.Shape GV.Octagon]
                                                     else [GV.Shape GV.BoxShape]
                        _ -> []
                in  GV.Label label : (coloring ++ styling)
            , GV.fmtEdge          = \(a, b, e) ->
                (case simplifyEdgeLabel (edgeLabels a b) of
                    [] -> []
                    [LGNameRelation Same] -> [GV.style GV.bold, GV.Weight (GV.Dbl 0.7)]
                    [LGNameRelation Better] -> [GV.style GV.dashed, GV.Weight (GV.Dbl 0.5)]
                    [LGAppliesTo] -> [GV.Weight (GV.Dbl 0.5)]
                    [LGImpliedBy] -> [GV.Weight (GV.Dbl 0.2)]
                    edgeLabels' -> [ GV.Label (GV.toLabelValue . unlines . map show $ edgeLabels') ]
                ) ++ getColorOfEdge (a, b, e)
            }
    in (GV.graphToDot params graph) {
            GV.strictGraph = True -- If True, no multiple edges are drawn.
        }

getDigraph :: [G.Node] -> [G.Node] -> [G.Node] -> LicenseGraphM (GV.DotGraph G.Node)
getDigraph mainLNs sameLNs otherLNs = MTL.gets (\g -> computeDigraph g mainLNs sameLNs otherLNs)

renderDot :: String -> GV.DotGraph G.Node -> FilePath -> IO FilePath
renderDot layout digraph dot = do
    let format = GV.Svg
    createParentDirectoryIfNotExists dot
    debugM "genGraphViz" $ "write dot to " ++ dot
    GV.writeDotFile dot digraph
    debugM "genGraphViz" "runGraphvizCommand"
    let command = case layout of
                    "fdp" -> GV.Fdp
                    "dot" -> GV.Dot
                    _ -> GV.Fdp
    res <- Ex.try $ GV.runGraphvizCommand command digraph format (dot <.> show format)
    case res of
        Left (Ex.SomeException e) -> fail $ "failed to convert dot to "++ show format ++ ": " ++ show e
        Right svg -> do
            debugLogIO $ "wrote SVG " ++ svg
            return svg

writeGraphViz :: [G.Node] -> [G.Node] -> [G.Node] -> FilePath -> LicenseGraphM ()
writeGraphViz mainLNs sameLNs otherLNs dot = do
    debugLog $ "generate " ++ dot
    digraph <- getDigraph mainLNs sameLNs otherLNs
    _ <- MTL.liftIO $ renderDot "fdp" digraph dot
    pure ()

genGraphViz :: [G.Node] -> [G.Node] -> [G.Node] -> LicenseGraphM LT.Text
genGraphViz mainLNs sameLNs otherLNs = do
    lift $ debugM "genGraphViz" "getDigraph"
    digraph <- getDigraph mainLNs sameLNs otherLNs
    MTL.liftIO $ do
        Temp.withSystemTempDirectory "genGraphViz" $ \tmpdir -> do
            debugM "genGraphViz" "renderDigraph"
            svg <- renderDot "fdp" digraph (tmpdir </> "dot")
            debugM "genGraphViz" "done renderDigraph"
            LT.readFile svg
