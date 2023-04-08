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
            focus [] ((V.singleton . LGName) lic) $
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

formHtml :: [S.Param] -> LicenseGraph -> [Origin] -> IO H.Html
formHtml params licenseGraph origins = do
    let paramMap = Map.fromList params
        licRaw = Map.findWithDefault "BSD-3-Clause" "license" paramMap
        lic = (fromText . T.toStrict) licRaw :: LicenseName
        enabledOrigins = case (map (Origin . T.unpack . fst) . filter (\(_,value) -> value == "on")) params of
            [] -> origins
            enabledOrigins -> enabledOrigins
        allLicenseNames = getLicenseGraphLicenseNames licenseGraph

    debugLogIO ("params=" ++ show params)
    debugLogIO ("licRaw=" ++ show licRaw)
    debugLogIO ("lic=" ++ show lic)
    debugLogIO ("enabledOrigins=" ++ show enabledOrigins)

    ((subgraph,lnsubgraph,svg),_) <-
        runLicenseGraphM' licenseGraph $
            focus enabledOrigins ((V.singleton . LGName) lic) $ do
                MTL.gets ((,,) . _gr)
                     <*> getLicenseNameGraph
                     <*> (do 
                        when ("on" == Map.findWithDefault "" "onlyLNs" paramMap) $
                            MTL.modify (\lg@LicenseGraph{_gr=gr} -> lg{_gr=G.labfilter (\case
                                                                                            LGName _ -> True
                                                                                            _ -> False) gr})
                        genGraphViz
                     )
    let facts = (mapMaybe (\case
                               LGFact f -> Just f
                               _ -> Nothing
                           . snd) . G.labNodes) subgraph

    let allPotentialLicenseNames = (map snd . G.labNodes) lnsubgraph

    return . H.html $ do
            H.head $ do
                H.title (H.toMarkup ("ldbcollector-haskell: " <> licRaw))
                H.link H.! A.rel "stylesheet" H.! A.href "https://unpkg.com/normalize.css@8.0.1/normalize.css"
                H.link H.! A.rel "stylesheet" H.! A.href "/styles.css"
                H.script H.! A.src "https://unpkg.com/panzoom@9.4.0/dist/panzoom.min.js" $
                    pure ()
            H.body $ do
                H.div H.! A.id "svgGraph" $ do
                    H.preEscapedToMarkup svg
                H.div H.! A.id "content" $ do
                    H.header $ do
                        H.h1 (H.toMarkup licRaw)
                        H.form H.! A.action "" $ do
                            H.input H.! A.name "license" H.! A.id "license" H.! A.value (H.toValue licRaw) H.! A.list "licenses"
                            H.datalist H.! A.id "licenses" $
                                mapM_ (\license -> H.option H.! A.value (fromString $ show license) $ pure ()) allLicenseNames
                            H.h4 "Origins"
                            H.ul $
                                mapM_ (\(Origin origin) -> H.li $ do
                                        if Origin origin `elem` enabledOrigins
                                            then H.input H.! A.type_ "checkbox" H.! A.name (fromString origin) H.! A.value "on" H.! A.checked "checked"
                                            else H.input H.! A.type_ "checkbox" H.! A.name (fromString origin) H.! A.value "on"
                                        H.label H.! A.for (fromString origin) $ fromString origin
                                    ) origins
                            H.h4 "Options"
                            H.ul $ do
                                H.li $ do
                                    if "on" == Map.findWithDefault "" "onlyLNs" paramMap
                                        then H.input H.! A.type_ "checkbox" H.! A.name "onlyLNs" H.! A.value "on" H.! A.checked "checked"
                                        else H.input H.! A.type_ "checkbox" H.! A.name "onlyLNs" H.! A.value "on"
                                    H.label H.! A.for (fromString "onlyLNs") $ fromString "onlyLNs"
                            H.input H.! A.type_ "submit" H.! A.value "reload" H.! A.name "reload"
                    H.div H.! A.id "popup" $ do
                        H.input H.! A.type_ "checkbox" H.! A.id "popupCheckbox"
                        H.div $ do
                            H.ul $ mapM_ (H.li . fromString . show) allPotentialLicenseNames
                            H.ul $ mapM_ (\fact -> H.li $ do
                                H.h3 (H.toMarkup (getFactId fact))
                                -- H.pre (H.toMarkup (let
                                --                     onerror _ _ = Just '_'
                                --                 in Enc.decodeUtf8With onerror (BL.toStrict (encodePretty fact))))
                                ) facts
                            H.pre $
                                H.toMarkup (G.prettify lnsubgraph)
                H.script $ do
                    "var element = document.querySelector('#svgGraph');"
                    "var instance = panzoom(element, {"
                    "    zoomSpeed: 0.065,"
                    "    filterKey: function(/* e, dx, dy, dz */) {return true;}"
                    "});"
                    "const checkbox = document.getElementById('popupCheckbox');"
                    "checkbox.addEventListener('change', (event) => {"
                    "   if (event.currentTarget.checked) {"
                    "    instance.pause();"
                    "  } else {"
                    "    instance.resume();"
                    "  }"
                    "});"

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
            get "/svg/:lic" $ do
                lic <- fromString <$> param "lic"
                svg <- liftAndCatchIO $ genSvg tmpdir lic licenseGraph
                file svg