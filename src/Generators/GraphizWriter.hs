{-# LANGUAGE OverloadedStrings #-}
-- | see: https://github.com/ReneNyffenegger/about-Graphviz/blob/master/examples/nested-clusters.dot
module Generators.GraphizWriter
  ( writeGraphizs
  ) where

import qualified Prelude as P
import           MyPrelude

import           Data.GraphViz as G hiding (DotGraph)
-- -- import           Data.GraphViz.Types
import           Data.GraphViz.Types.Generalised as G
import           Data.GraphViz.Types.Monadic as G
import           Data.GraphViz.Commands as G
import           Data.GraphViz.Attributes.Complete as G
import           Data.GraphViz.Attributes.Colors as G
import qualified Data.Set as S
import           Data.Set (Set)
import qualified Data.Text.Lazy as T
import           Control.Monad.State

import           Model.License
import           Model.LicenseClusterer (LicenseClusterTree (..), lctToNames)

lctToGraph :: [LicenseName] -> LicenseName -> LicenseClusterTree -> DotGraph LicenseName
lctToGraph primaryNames shortname lct = let
    mkNode namesFromPrev i name = let
        nodeName = name ++ "("++ show i ++ ")"
        label =  Label (StrLabel (T.pack name))
      in if name `elem` primaryNames
         then if name == shortname
              then node nodeName [color SpringGreen, label]
              else node nodeName [color Orange, label]
         else if name `S.member` namesFromPrev
              then node nodeName [color LightGray, label]
              else node nodeName [label]
    lctToGraph' :: Set LicenseName -> LicenseClusterTree -> State Int (Dot LicenseName)
    lctToGraph' namesFromPrev (LCTLeaf names) = do
      i <- get
      put (i + 1)
      return (cluster (Num (Int i)) $ do
               graphAttrs [style filled, color LightGray]
               nodeAttrs [style filled, color White]
               mapM_ (mkNode namesFromPrev i) names)
    lctToGraph' _ (LCTNode prev childs) = do
      i <- get
      put (i + 1)
      dotPrev <- lctToGraph' S.empty prev
      let namesFromPrev = lctToNames prev
      dotChilds <- mapM (lctToGraph' namesFromPrev) childs
      return (cluster (Num (Int i)) $ do
                 dotPrev
                 mconcat dotChilds)
  in digraph (Str (T.pack shortname)) $
     do
       graphAttrs [RankDir FromLeft]
       evalState (lctToGraph' S.empty lct) 0

writeGraphizs :: FilePath -> [(LicenseName, LicenseClusterTree)] -> IO()
writeGraphizs outBaseDirectory trees = let
    outDirectory = outBaseDirectory </> "dot"
    primaryNames = map P.fst trees
  in do
  isInstalled <- isGraphvizInstalled
  when isInstalled (do
                       createDirectoryIfNotExists outDirectory
                       mapM_ (\(shortname, lct) -> writeGraphiz outDirectory primaryNames shortname lct) trees)

writeGraphiz :: FilePath -> [LicenseName] -> LicenseName -> LicenseClusterTree -> IO ()
writeGraphiz outDirectory primaryNames shortname lct = let
    outFile = outDirectory </> shortname ++ ".svg"
    graph = lctToGraph primaryNames shortname lct
  in do
    runGraphviz graph Svg outFile
    return ()
