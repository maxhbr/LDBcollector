{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE LambdaCase #-}
module Ldbcollector.Server
    ( serve
    ) where

import           Ldbcollector.Model
import           Ldbcollector.Sink.GraphViz
import           Ldbcollector.Sink.Metrics

import qualified Data.Vector                        as V

import qualified Control.Monad.State                as MTL
import qualified Data.Text.Lazy                     as T
import qualified Data.Text.Encoding                 as Enc
import qualified System.IO.Temp                     as Temp
import qualified Text.Blaze.Html.Renderer.Text      as BT
import qualified Text.Blaze.Html5                   as B
import qualified Text.Blaze.Html5.Attributes        as B hiding (span, title)
import qualified Data.ByteString.Lazy as BL

import qualified Data.Graph.Inductive.Basic        as G
import qualified Data.Graph.Inductive.Graph        as G

import           Web.Scotty as S
import qualified Network.Wai.Handler.Warp as Warp

myOptions :: S.Options
myOptions = S.Options 1 (Warp.setPort 3000 (Warp.setFileInfoCacheDuration 3600 (Warp.setFdCacheDuration 3600 Warp.defaultSettings)))

genSvg :: FilePath -> LicenseName -> LicenseGraph -> IO FilePath
genSvg tmpdir lic licenseGraph = do
    let dot = tmpdir </> show lic <.> "dot"
    let svg = dot <.> "Svg"
    svgExists <- doesFileExist svg
    unless svgExists $ do
        _ <- runLicenseGraphM' licenseGraph $
            focus ((V.singleton . LGName) lic) $
                writeGraphViz dot
        return ()
    return svg

serve :: LicenseGraphM ()
serve = do

    licenseGraph <- MTL.get
    let names = getLicenseGraphLicenseNames licenseGraph
    clusters <- getClusters

    lift $ Temp.withSystemTempDirectory "ldbcollector-haskell" $ \tmpdir -> do
        putStrLn $ "tmpdir=" ++ tmpdir
        scottyOpts myOptions $ do

            get "/" $ do
                let page = B.html $ do
                        B.head $ B.title "ldbcollector-haskell"
                        B.body $ do
                            B.ul $ mapM_ (\cluster ->
                                B.li (B.ul $ mapM_ (B.li . (\n -> B.a B.! B.href ((B.toValue . ("./svg/"++)) n) $ B.toMarkup n) . show) cluster)) clusters
                html (BT.renderHtml page)

            get "/html/:lic" $ do
                licRaw <- param "lic"
                let lic = fromString licRaw :: LicenseName
                ((subgraph,lnsubgraph),_) <- liftAndCatchIO $
                    runLicenseGraphM' licenseGraph $
                        focus ((V.singleton . LGName) lic) $ do
                            subgraph <- MTL.gets _gr
                            lnsubgraph <- getLicenseNameGraph
                            return (subgraph, lnsubgraph)
                let facts = (mapMaybe (\case
                                           LGFact f -> Just f
                                           _ -> Nothing) . map snd . G.labNodes) subgraph
                let page = B.html $ do
                        B.head $ B.title (B.toMarkup ("ldbcollector-haskell: " <> licRaw))
                        B.body $ do
                            B.h1 (B.toMarkup licRaw)
                            -- B.iframe B.! B.src (B.toValue $ "/svg/" <> licRaw) B.! B.alt "svg"
                            B.ul $ mapM_ (\fact -> B.li $ do
                                B.h3 (B.toMarkup (getFactId fact))
                                B.pre (B.toMarkup (let
                                                    onerror _ _ = Just '_'
                                                in Enc.decodeUtf8With onerror (BL.toStrict (encodePretty fact))))
                                ) facts
                            B.pre $
                                B.toMarkup (G.prettify lnsubgraph)

                html (BT.renderHtml page)
                
            get "/svg/:lic" $ do
                licRaw <- param "lic"
                let lic = fromString licRaw :: LicenseName
                svg <- liftAndCatchIO $ genSvg tmpdir lic licenseGraph
                file svg