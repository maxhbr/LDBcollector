{-# LANGUAGE CPP #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE TemplateHaskell #-}
module Ldbcollector.Server
    ( serve
    ) where

import           Ldbcollector.Model
import           Ldbcollector.Sink.GraphViz
import           Ldbcollector.Sink.Metrics

import qualified Data.Vector                        as V

import qualified Control.Monad.State                as MTL
import qualified Data.Text.Lazy                     as T
import qualified Data.Text.Lazy.IO                  as T
import qualified Data.Text.Encoding                 as Enc
import qualified System.IO.Temp                     as Temp
import qualified Text.Blaze.Html.Renderer.Text      as BT
import qualified Text.Blaze.Html5                   as H
import qualified Text.Blaze.Html5.Attributes        as A
import qualified Data.ByteString.Lazy as BL
import qualified Data.ByteString
import qualified Data.Map as Map

import qualified Data.Graph.Inductive.Basic        as G
import qualified Data.Graph.Inductive.Graph        as G

import Data.FileEmbed (embedFile)
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

stylesheet :: Data.ByteString.ByteString
stylesheet = $(embedFile "src/assets/styles.css")


listPageAction :: [[LicenseName]] -> ActionM ()
listPageAction clusters = do
    let page = H.html $ do
            H.head $ H.title "ldbcollector-haskell"
            H.body $ do
                H.ul $ mapM_ (\cluster ->
                    H.li (H.ul $ mapM_ (H.li . (\n -> H.a H.! A.href ((H.toValue . ("./svg/"++)) n) $ H.toMarkup n) . show) cluster)) clusters
    html (BT.renderHtml page)

genDetailsHtml :: String -> LicenseGraph -> [Origin] -> IO H.Html
genDetailsHtml licRaw licenseGraph origins = do
    let lic = fromString licRaw :: LicenseName
    ((subgraph,lnsubgraph),_) <-
        runLicenseGraphM' licenseGraph $
            focus ((V.singleton . LGName) lic) $ do
                subgraph <- MTL.gets _gr
                lnsubgraph <- getLicenseNameGraph
                return (subgraph, lnsubgraph)
    let facts = (mapMaybe (\case
                               LGFact f -> Just f
                               _ -> Nothing
                           . snd) . G.labNodes) subgraph
    return . H.html $ do
            H.head $ do
                H.title (H.toMarkup ("ldbcollector-haskell: " <> licRaw))
                H.link H.! A.rel "stylesheet" H.! A.href "https://unpkg.com/normalize.css@8.0.1/normalize.css"
                H.link H.! A.rel "stylesheet" H.! A.href "/styles.css"
                H.script H.! A.src "https://unpkg.com/panzoom@9.4.0/dist/panzoom.min.js" $
                    pure ()
            H.body $ do
                -- H.iframe
                --     H.! H.id "svgGraph" 
                --     H.! H.width "100%" 
                --     H.! H.height "100%"
                --     H.! H.src (H.toValue $ "/svg/" <> licRaw)
                --     H.! H.alt "svg" $
                --         pure ()
                -- H.div H.! H.id "svgWrapper" $ do
                H.object H.! A.id "svgGraph" H.! A.type_ "image/svg+xml" H.! A.data_ (H.toValue $ "/svg/" <> licRaw) $
                    pure ()
                H.div H.! A.id "content" $ do
                    H.header $
                        H.h1 (H.toMarkup licRaw)

                    H.form H.! A.action (H.toValue licRaw) $ do
                        H.input H.! A.name "license" H.! A.id "license"
                        mapM_ (\(Origin origin) -> do
                                H.input H.! A.type_ "checkbox" H.! A.name (fromString origin) H.! A.value (fromString origin) H.! A.checked "checked"
                                H.label H.! A.for (fromString origin) $ fromString origin
                            ) origins
                        H.input H.! A.type_ "submit" H.! A.value "reload" H.! A.name "reload"
                    -- H.div H.! H.id "content" $ do
                    --     H.ul $ mapM_ (\fact -> H.li $ do
                    --         H.h3 (H.toMarkup (getFactId fact))
                    --         H.pre (H.toMarkup (let
                    --                             onerror _ _ = Just '_'
                    --                         in Enc.decodeUtf8With onerror (BL.toStrict (encodePretty fact))))
                    --         ) facts
                    --     H.pre $
                    --         H.toMarkup (G.prettify lnsubgraph)
                H.script $ do
                    "var element = document.querySelector('#svgGraph');"
                    "panzoom(element);"

formHtml :: [S.Param] -> LicenseGraph -> [Origin] -> IO H.Html
formHtml params licenseGraph origins = do
    let paramMap = Map.fromList params
        licRaw = Map.findWithDefault "BSD-3-Clause" "license" paramMap
        lic = (fromText . T.toStrict) licRaw :: LicenseName
        enableOrigins = case (map (Origin . T.unpack . fst) . filter (\(_,value) -> value == "on")) params of
            [] -> origins
            enableOrigins -> enableOrigins
        allLicenseNames = getLicenseGraphLicenseNames licenseGraph

    debugLogIO ("params=" ++ show params)
    debugLogIO ("licRaw=" ++ show licRaw)
    debugLogIO ("lic=" ++ show lic)
    debugLogIO ("enableOrigins=" ++ show enableOrigins)

    ((subgraph,lnsubgraph,svg),_) <-
        runLicenseGraphM' licenseGraph $
            focusAndFilter ((V.singleton . LGName) lic) enableOrigins $ do
                MTL.gets ((,,) . _gr)
                     <*> getLicenseNameGraph
                     <*> genGraphViz

    return . H.html $ do
            H.head $ do
                H.title (H.toMarkup ("ldbcollector-haskell: " <> licRaw))
                H.link H.! A.rel "stylesheet" H.! A.href "https://unpkg.com/normalize.css@8.0.1/normalize.css"
                H.link H.! A.rel "stylesheet" H.! A.href "/styles.css"
                H.script H.! A.src "https://unpkg.com/panzoom@9.4.0/dist/panzoom.min.js" $
                    pure ()
            H.body $ do
                -- H.object H.! A.id "svgGraph" H.! A.type_ "image/svg+xml" H.! A.data_ (H.toValue $ "/svg/" <> licRaw) $
                --     pure ()
                H.div H.! A.id "svgGraph" $ do
                    H.preEscapedToMarkup svg
                H.div H.! A.id "content" $ do
                    H.header $
                        H.h1 (H.toMarkup licRaw)

                    H.form H.! A.action "" $ do
                        H.input H.! A.name "license" H.! A.id "license" H.! A.value (H.toValue licRaw) H.! A.list "licenses"
                        H.datalist H.! A.id "licenses" $
                            mapM_ (\license -> H.option H.! A.value (fromString $ show license) $ pure ()) allLicenseNames
                        mapM_ (\(Origin origin) -> do
                                if Origin origin `elem` enableOrigins
                                    then H.input H.! A.type_ "checkbox" H.! A.name (fromString origin) H.! A.value "on" H.! A.checked "checked"
                                    else H.input H.! A.type_ "checkbox" H.! A.name (fromString origin) H.! A.value "on"
                                H.label H.! A.for (fromString origin) $ fromString origin
                            ) origins
                        H.input H.! A.type_ "submit" H.! A.value "reload" H.! A.name "reload"
                    -- H.div H.! H.id "content" $ do
                    --     H.ul $ mapM_ (\fact -> H.li $ do
                    --         H.h3 (H.toMarkup (getFactId fact))
                    --         H.pre (H.toMarkup (let
                    --                             onerror _ _ = Just '_'
                    --                         in Enc.decodeUtf8With onerror (BL.toStrict (encodePretty fact))))
                    --         ) facts
                    --     H.pre $
                    --         H.toMarkup (G.prettify lnsubgraph)
                H.script $ do
                    "var element = document.querySelector('#svgGraph');"
                    "panzoom(element);"

serve :: LicenseGraphM ()
serve = do
    licenseGraph <- MTL.get
    let names = getLicenseGraphLicenseNames licenseGraph
    clusters <- getClusters
    origins <- MTL.gets (nub . map fst . Map.keys . _facts)

    infoLog "Start server on port 3000..."
    lift $ Temp.withSystemTempDirectory "ldbcollector-haskell" $ \tmpdir -> do
        putStrLn $ "tmpdir=" ++ tmpdir
        scottyOpts myOptions $ do
            get "/styles.css" $ raw (BL.fromStrict stylesheet)
            get "/" $ do
                params <- S.params
                page <- liftAndCatchIO $ formHtml params licenseGraph origins
                html (BT.renderHtml page)
            get "/clusters" $ listPageAction clusters
            get "/html/:lic" $ do
                licRaw <- param "lic"
                page <- liftAndCatchIO $ genDetailsHtml licRaw licenseGraph origins
                html (BT.renderHtml page)
            get "/svg/:lic" $ do
                lic <- fromString <$> param "lic"
                svg <- liftAndCatchIO $ genSvg tmpdir lic licenseGraph
                file svg