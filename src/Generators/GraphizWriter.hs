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
import           Model.LicenseClusterer (LicenseClusterTree (..))

lctToGraph :: [LicenseName] -> LicenseName -> LicenseClusterTree -> DotGraph LicenseName
lctToGraph primaryNames shortname lct = let
    mkNode i name = let
        nodeName = name ++ "("++ show i ++ ")"
        label =  Label (StrLabel (T.pack name))
      in if name `elem` primaryNames
         then if name == shortname
              then node nodeName [color SpringGreen, label]
              else node nodeName [color Orange, label]
         else node nodeName [label]
    lctToGraph' :: LicenseClusterTree -> State Int (Dot LicenseName)
    lctToGraph' (LCTLeaf names) = do
      i <- get
      put (i + 1)
      return (cluster (Num (Int i)) $ do
               -- graphAttrs [textLabel "process #1"]
               graphAttrs [style filled, color LightGray]
               nodeAttrs [style filled, color White]
               mapM_ (mkNode i) names)
    lctToGraph' (LCTNode prev childs) = do
      i <- get
      put (i + 1)
      dotPrev <- lctToGraph' prev
      dotChilds <- mapM lctToGraph' childs
      return (cluster (Num (Int i)) $ do
                 dotPrev
                 mconcat dotChilds)
  in digraph (Str (T.pack shortname)) (evalState (lctToGraph' lct) 0)

writeGraphizs :: FilePath -> [(LicenseName, LicenseClusterTree)] -> IO()
writeGraphizs outBaseDirectory trees = let
    outDirectory = outBaseDirectory </> "dot"
    primaryNames = map (\(ln,_) -> ln) trees
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
