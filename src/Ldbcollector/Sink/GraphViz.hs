{-# LANGUAGE CPP #-}
{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE OverloadedStrings #-}

module Ldbcollector.Sink.GraphViz
  ( writeGraphViz,
    genGraphViz,
    getDigraph,
    Digraph,
    digraphToText,
    rederDotToText,
  )
where

import Control.Exception qualified as Ex
import Control.Monad.State qualified as MTL
import Data.Graph.Inductive.Graph qualified as G
import Data.Graph.Inductive.Monad qualified as G
import Data.Graph.Inductive.PatriciaTree qualified as G
import Data.Graph.Inductive.Query.DFS qualified as G
import Data.GraphViz qualified as GV
import Data.GraphViz.Attributes.Colors qualified as GVH
import Data.GraphViz.Attributes.Colors.SVG qualified as GVH
import Data.GraphViz.Attributes.Complete qualified as GV
import Data.GraphViz.Attributes.HTML qualified as GVH
import Data.GraphViz.Commands.IO qualified as GV
import Data.GraphViz.Printing qualified as GV
import Data.HashMap.Internal.Strict qualified as HMap
import Data.Map qualified as Map
import Data.Text.Lazy qualified as LT
import Data.Text.Lazy.IO qualified as LT
import Data.Vector qualified as V
import Ldbcollector.Model
import System.IO.Temp qualified as Temp
import Text.Wrap qualified as TW

type Digraph = GV.DotGraph G.Node

factIdToLabelValue :: FactId -> GV.Label
factIdToLabelValue (FactId ty hash) = GV.toLabelValue (ty ++ "\n" ++ hash)

textToMultilines :: Text -> GVH.Text
textToMultilines = intersperse (GVH.Newline []) . map GVH.Str . LT.lines . LT.fromStrict . TW.wrapText TW.defaultWrapSettings 80

licenseStatementToLabelValue :: LicenseStatement -> GV.Label
licenseStatementToLabelValue (LicenseStatement stmt) = GV.toLabelValue stmt
licenseStatementToLabelValue (LicenseUrl url) = GV.toLabelValue url
licenseStatementToLabelValue (LicenseText txt) = GV.toLabelValue ("$TEXT" :: Text)
licenseStatementToLabelValue (LicenseRule txt) = GV.toLabelValue ("$RULE" :: Text)
licenseStatementToLabelValue (LicenseComment txt) = GV.toLabelValue (TW.wrapText TW.defaultWrapSettings 80 txt)
licenseStatementToLabelValue (LicensePCLR pclr) =
  let header =
        GVH.Cells
          [ GVH.LabelCell [] (GVH.Text [GVH.Str "Permissions"]),
            GVH.LabelCell [] (GVH.Text [GVH.Str "Conditions"]),
            GVH.LabelCell [] (GVH.Text [GVH.Str "Limitations"]),
            GVH.LabelCell [] (GVH.Text [GVH.Str "Restrictions"])
          ]
      linesToContent :: [Text] -> GVH.Cell
      linesToContent = GVH.LabelCell [] . GVH.Text . intersperse newline . map (GVH.Str . LT.fromStrict)
      newline = GVH.Newline []
      content = GVH.Cells (map linesToContent [_permissions pclr, _conditions pclr, _limitations pclr, _restrictions pclr])
   in GV.HtmlLabel . GVH.Table $ GVH.HTable Nothing [] [header, content]
#if 0
licenseStatementToLabelValue (LicenseCompatibilities compatibilities) = let
            mkLine (LicenseCompatibility other compatibility explanation) =
                GVH.Cells [ GVH.LabelCell [] (GVH.Text [GVH.Str . LT.pack $ show other])
                          , GVH.LabelCell [] (GVH.Text [GVH.Str $ LT.pack compatibility])
                        --   , GVH.LabelCell [] (GVH.Text [GVH.Str $ LT.fromStrict explanation])
                          ]
        in GV.HtmlLabel . GVH.Table $ GVH.HTable Nothing [] (map mkLine compatibilities)
#else
licenseStatementToLabelValue (LicenseCompatibilities _) = GV.toLabelValue ("$COMPATIBILITIES" :: Text)
#endif
licenseStatementToLabelValue (LicenseRating rating) =
  let color = GVH.Color . GVH.SVGColor $ case rating of
        NegativeLicenseRating {} -> GVH.DarkRed
        NeutralLicenseRating {} -> GVH.Black
        PositiveLicenseRating {} -> GVH.ForestGreen
      ns = case rating of
        NegativeLicenseRating ns _ _ -> ns
        NeutralLicenseRating ns _ _ -> ns
        PositiveLicenseRating ns _ _ -> ns
      description = maybe [] ((GVH.Newline [] :) . textToMultilines) $
        case rating of
          NegativeLicenseRating _ _ (Just desc) -> Just desc
          NeutralLicenseRating _ _ (Just desc) -> Just desc
          PositiveLicenseRating _ _ (Just desc) -> Just desc
          _ -> Nothing
   in GV.HtmlLabel . GVH.Text $
        [ GVH.Str (fromString ns),
          GVH.Str ": ",
          GVH.Format GVH.Bold [GVH.Font [color] [(GVH.Str . LT.fromStrict . unLicenseRating) rating]]
        ]
          ++ description
licenseStatementToLabelValue statement = (GV.StrLabel . LT.pack . show) statement

simplifyEdgeLabel :: [LicenseGraphEdge] -> [LicenseGraphEdge]
simplifyEdgeLabel [] = []
simplifyEdgeLabel [a] = [a]
simplifyEdgeLabel as =
  let getAllLnRelations [] = Just []
      getAllLnRelations (LGNameRelation r : as) = fmap (r :) (getAllLnRelations as)
      getAllLnRelations _ = Nothing
   in case getAllLnRelations as of
        Just lns ->
          if Same `elem` lns
            then [LGNameRelation Same]
            else
              if Better `elem` lns
                then [LGNameRelation Better]
                else as
        _ -> nub as

generateColorMapping :: (Show a, Ord a, Eq a) => [a] -> Map.Map a GV.Color
generateColorMapping =
  let colors =
        cycle $
          map
            (\(r, g, b) -> GV.RGB r g b)
            [ (0, 135, 108), -- #00876c
              (55, 148, 105), -- #379469
              (88, 160, 102), -- #58a066
              (120, 171, 99), -- #78ab63
              (152, 181, 97), -- #98b561
              (184, 191, 98), -- #b8bf62
              (218, 199, 103), -- #dac767
              (222, 178, 86), -- #deb256
              (224, 157, 75), -- #e09d4b
              (225, 135, 69), -- #e18745
              (224, 111, 69), -- #e06f45
              (220, 87, 74), -- #dc574a
              (212, 61, 81) -- #d43d51
            ]
   in Map.fromList . (`zip` colors) . sortOn show . nub

computeDigraph :: LicenseGraph -> [G.Node] -> [G.Node] -> [G.Node] -> (GV.DotGraph G.Node, SourceRef -> GV.Color)
computeDigraph (LicenseGraph {_gr = graph, _facts = facts}) mainLNs sameLNs otherLNs =
  let factColoringMap = generateColorMapping ((map fst . Map.keys) facts)
      typeColoringLookup source = Map.findWithDefault (GV.RGB 0 0 0) source factColoringMap

      getSourcesOfNode :: G.Node -> [SourceRef]
      getSourcesOfNode n =
        ( nub
            . sort
            . mapMaybe
              ( \((source, _), (nodes, _)) ->
                  if n `elem` nodes
                    then Just source
                    else Nothing
              )
            . Map.assocs
        )
          facts

      getColorOfNode :: (G.Node, Maybe LicenseGraphNode) -> GV.Attributes
      getColorOfNode (n, Just (LGName _)) =
        case getSourcesOfNode n of
          [source] -> [(GV.Color . (: []) . (`GV.WC` Nothing) . typeColoringLookup) source]
          [] -> [GV.Style [GV.SItem GV.Dashed []]]
          _ -> []
      getColorOfNode (n, Just (LGFact _)) =
        case getSourcesOfNode n of
          [source] ->
            [ GV.FontColor (GV.X11Color GV.Gray),
              (GV.Color . (: []) . (`GV.WC` Nothing) . typeColoringLookup) source
            ]
          [] -> [GV.Style [GV.SItem GV.Dashed []]]
          _ -> []
      getColorOfNode _ = []

      getSourcesOfEdge :: G.Edge -> [SourceRef]
      getSourcesOfEdge n =
        ( nub
            . sort
            . mapMaybe
              ( \((source, _), (_, edges)) ->
                  if n `elem` edges
                    then Just source
                    else Nothing
              )
            . Map.assocs
        )
          facts

      getColorOfEdge :: G.LEdge LicenseGraphEdge -> GV.Attributes
      getColorOfEdge edge =
        let potentialE = (fmap G.toEdge . find (== edge) . G.labEdges) graph
         in case potentialE of
              Just e -> case getSourcesOfEdge e of
                [source] -> [(GV.Color . (: []) . (`GV.WC` Nothing) . typeColoringLookup) source]
                [] -> []
                _ -> []
              Nothing -> []

      edgeLabels a b =
        ( map (\(_, _, l) -> l)
            . filter (\(a', b', _) -> a == a' && b == b')
            . G.labEdges
        )
          graph
      params =
        GV.nonClusteredParams
          { GV.isDirected = True,
            GV.globalAttributes =
              [ GV.NodeAttrs [GV.Shape GV.BoxShape],
                GV.GraphAttrs [GV.Splines GV.Curved]
              ],
            GV.fmtNode = \(n, l) ->
              let nodeLabel = graph `G.lab` n
                  label = case nodeLabel of
                    Just (LGName name) -> GV.toLabelValue (show name)
                    Just (LGStatement stmt) -> licenseStatementToLabelValue stmt
                    Just (LGFact fact) -> factIdToLabelValue (getFactId fact)
                    Just nodeLabel' -> GV.toLabelValue (show nodeLabel')
                    Nothing -> GV.toLabelValue ("(/)" :: Text)
                  coloring = getColorOfNode (n, nodeLabel)
                  styling = case nodeLabel of
                    Just (LGStatement _) ->
                      [ GV.FillColor [GV.WC (GV.X11Color GV.Beige) (Just 1)],
                        GV.Shape GV.PlainText
                      ]
                    Just (LGFact _) ->
                      [ GV.FillColor [GV.WC (GV.X11Color GV.Beige) (Just 1)],
                        GV.Shape GV.Ellipse
                      ]
                    Just (LGName _) ->
                      if n `elem` mainLNs
                        then [GV.Shape GV.TripleOctagon]
                        else
                          if n `elem` sameLNs
                            then [GV.Shape GV.DoubleOctagon]
                            else
                              if n `elem` otherLNs
                                then [GV.Shape GV.Octagon]
                                else [GV.Shape GV.BoxShape]
                    _ -> []
               in GV.Label label : (coloring ++ styling),
            GV.fmtEdge = \(a, b, e) ->
              ( case simplifyEdgeLabel (edgeLabels a b) of
                  [] -> []
                  [LGNameRelation Same] -> [GV.style GV.bold, GV.ArrowHead $ GV.AType [(GV.noMods, GV.Vee)], GV.Weight (GV.Dbl 0.7)]
                  [LGNameRelation Better] -> [GV.style GV.dashed, GV.ArrowHead $ GV.AType [(GV.noMods, GV.Vee)], GV.Weight (GV.Dbl 0.5)]
                  [LGAppliesTo] -> [GV.Weight (GV.Dbl 0.5)]
                  [LGImpliedBy] -> [GV.Weight (GV.Dbl 0.2)]
                  edgeLabels' -> [GV.Label (GV.toLabelValue . unlines . map show $ edgeLabels')]
              )
                ++ getColorOfEdge (a, b, e)
          }
   in ( (GV.graphToDot params graph)
          { GV.strictGraph = True -- If True, no multiple edges are drawn.
          },
        typeColoringLookup
      )

getDigraph :: [G.Node] -> [G.Node] -> [G.Node] -> LicenseGraphM (Digraph, SourceRef -> GV.Color)
getDigraph mainLNs sameLNs otherLNs = MTL.gets (\g -> computeDigraph g mainLNs sameLNs otherLNs)

digraphToText :: Digraph -> LT.Text
digraphToText = GV.printDotGraph

renderDot :: String -> Digraph -> FilePath -> IO FilePath
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
  res <- Ex.try $ GV.runGraphvizCommand command digraph format (dot -<.> show format)
  case res of
    Left (Ex.SomeException e) -> fail $ "failed to convert dot to " ++ show format ++ ": " ++ show e
    Right svg -> do
      debugLogIO $ "wrote SVG " ++ svg
      return svg

rederDotToText :: String -> Digraph -> IO LT.Text
rederDotToText layout digraph = do
  MTL.liftIO $ do
    Temp.withSystemTempDirectory "genGraphViz" $ \tmpdir -> do
      debugM "genGraphViz" "renderDigraph"
      svg <- renderDot layout digraph (tmpdir </> "dot")
      debugM "genGraphViz" "done renderDigraph"
      LT.readFile svg

writeGraphViz :: [G.Node] -> [G.Node] -> [G.Node] -> FilePath -> LicenseGraphM ()
writeGraphViz mainLNs sameLNs otherLNs dot = do
  debugLog $ "generate " ++ dot
  digraph <- fst <$> getDigraph mainLNs sameLNs otherLNs
  _ <- MTL.liftIO $ renderDot "fdp" digraph dot
  pure ()

genGraphViz :: [G.Node] -> [G.Node] -> [G.Node] -> LicenseGraphM LT.Text
genGraphViz mainLNs sameLNs otherLNs = do
  lift $ debugM "genGraphViz" "getDigraph"
  digraph <- fst <$> getDigraph mainLNs sameLNs otherLNs
  MTL.liftIO $ do
    Temp.withSystemTempDirectory "genGraphViz" $ \tmpdir -> do
      debugM "genGraphViz" "renderDigraph"
      svg <- renderDot "fdp" digraph (tmpdir </> "dot")
      debugM "genGraphViz" "done renderDigraph"
      LT.readFile svg
