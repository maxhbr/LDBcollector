{-# LANGUAGE CPP               #-}
{-# LANGUAGE LambdaCase        #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE TemplateHaskell   #-}
module Ldbcollector.Server
    ( serve
    ) where

import           Ldbcollector.Model
import           Ldbcollector.Sink.GraphViz

import qualified Data.Vector                   as V

import qualified Control.Monad.State           as MTL
import qualified Data.ByteString
import qualified Data.ByteString.Lazy          as BL
import qualified Data.Map                      as Map
import qualified Data.Text.Encoding            as Enc
import qualified Data.Text.Lazy                as T
import qualified Data.Text.Lazy.IO             as T
import qualified System.IO.Temp                as Temp
import qualified Text.Blaze.Html.Renderer.Text as BT
import qualified Text.Blaze.Html5              as H
import qualified Text.Blaze.Html5.Attributes   as A

import qualified Data.Graph.Inductive.Basic    as G
import qualified Data.Graph.Inductive.Graph    as G

import           Data.FileEmbed                (embedFile)
import qualified Network.Wai.Handler.Warp      as Warp
import           Web.Scotty                    as S
import Text.Blaze.Html5.Attributes (onratechange)


class ParamMapC a where
    getLicRaw :: a -> T.Text
    getLic :: a -> LicenseName
    getIsExcludeStmts :: a -> Bool
    getEnabledSources :: a -> [SourceRef]
    isSourceEnabled :: a -> SourceRef -> Bool
newtype ParamMap = ParamMap {
        unParamMap :: Map.Map T.Text T.Text
    }
excludeStmts :: T.Text
excludeStmts = "excludeStmts"
instance ParamMapC ParamMap where
    getLicRaw = Map.findWithDefault "BSD-3-Clause" "license" . unParamMap
    getLic = fromText . T.toStrict . getLicRaw
    getIsExcludeStmts = ("on" ==) . Map.findWithDefault "off" excludeStmts . unParamMap
    getEnabledSources = map (Source . T.unpack . fst) . filter (\(_,value) -> value == "on") . Map.assocs . unParamMap
    isSourceEnabled pm s = s `elem` getEnabledSources pm

instance Show ParamMap where
    show pm = let
            assocs = (Map.assocs . unParamMap) pm
            licRaw = getLicRaw pm
            lic = getLic pm
            enabledSources = getEnabledSources pm
        in unlines [ "params=" ++ show assocs
                   , "licRaw=" ++ show licRaw
                   , "lic=" ++ show lic
                   , "enabledSources=" ++ show enabledSources
                   ]

evaluateParams :: [S.Param] -> IO ParamMap
evaluateParams  params = do
    let pm = (ParamMap . Map.fromList) params
    debugLogIO (show pm)
    return pm


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
                \(needleNames, sameNames, otherNames, _statements) -> do
                    writeGraphViz needleNames sameNames otherNames dot
        return ()
    return svg

stylesheet :: Data.ByteString.ByteString
stylesheet = $(embedFile "src/assets/styles.css")

scriptJs :: Data.ByteString.ByteString
scriptJs = $(embedFile "src/assets/script.js")

listPageAction :: [[LicenseName]] -> ActionM ()
listPageAction clusters = do
    let page = H.html $ do
            H.head $ H.title "ldbcollector-haskell"
            H.body $ do
                H.ul $ mapM_ (\cluster ->
                    H.li (H.ul $ mapM_ (H.li . (\n -> H.a H.! A.href ((H.toValue . ("./svg/"++)) n) $ H.toMarkup n) . show) cluster)) clusters
    html (BT.renderHtml page)

printFacts :: FactId -> LicenseGraph -> IO H.Html
printFacts factId licenseGraph = do
    (facts,_) <-
        runLicenseGraphM' licenseGraph $
            MTL.gets (filter (\(_,f) -> getFactId f == factId) . Map.keys . _facts)
    return . H.html $ do
        mapM_ (\(source,fact) -> do
            H.h1 (H.toMarkup (show source))
            H.h2 (H.toMarkup (show (getFactId fact)))
            toMarkup fact
            H.h3 "JSON"
            H.pre (H.toMarkup (let
                                onerror _ _ = Just '_'
                            in Enc.decodeUtf8With onerror (BL.toStrict (encodePretty fact))))) facts

conputeSubgraph :: LicenseGraph -> ParamMap -> IO (LicenseGraphType, LicenseNameGraphType, T.Text, [LicenseName], [LicenseName])
conputeSubgraph licenseGraph paramMap = do
    let licLN = LGName (getLic paramMap)
    fmap fst . runLicenseGraphM' licenseGraph $ do
            (subgraph,lnsubgraph,svg,sameNameNodes,otherNameNodes) <- focus (getEnabledSources paramMap) (V.singleton licLN) $
                \(needleNames, sameNames, otherNames, _statements) -> do
                    MTL.gets ((,,,,) . _gr)
                        <*> getLicenseNameGraph
                        <*> (do
                            when (getIsExcludeStmts paramMap) $
                                MTL.modify (\lg@LicenseGraph{_gr=gr} -> lg{_gr=G.labfilter (\case
                                                                                                LGName _ -> True
                                                                                                LGFact _ -> True
                                                                                                _ -> False) gr})
                            genGraphViz needleNames sameNames otherNames)
                        <*> pure sameNames
                        <*> pure otherNames
            let graphNodeToLn (Just (LGName ln)) = Just ln
                graphNodeToLn _ = Nothing
            sameNames <- catMaybes <$> mapM (\n -> MTL.gets (graphNodeToLn . (`G.lab` n) . _gr)) sameNameNodes
            otherNames <- catMaybes <$> mapM (\n -> MTL.gets (graphNodeToLn . (`G.lab` n) . _gr)) otherNameNodes
            return (subgraph,lnsubgraph,svg,sameNames,otherNames)

svgPage :: [S.Param] -> LicenseGraph -> IO T.Text
svgPage params licenseGraph = do
    paramMap <- evaluateParams params
    (_,_,svg,_,_) <- conputeSubgraph licenseGraph paramMap
    return svg

mainPage :: [S.Param] -> LicenseGraph -> IO H.Html
mainPage params licenseGraph = do

    let allLicenseNames = getLicenseGraphLicenseNames licenseGraph
    let allSources = (nub . map fst . Map.keys . _facts) licenseGraph

    paramMap <- evaluateParams params
    (subgraph,lnsubgraph,svg,sameNames,otherNames) <- conputeSubgraph licenseGraph paramMap

    let facts = (mapMaybe (\case
                               LGFact f -> Just f
                               _        -> Nothing
                           . snd) . G.labNodes) subgraph
    return . H.html $ do
            let licRaw = getLicRaw paramMap
            H.head $ do
                H.title (H.toMarkup ("ldbcollector-haskell: " <> licRaw))
                H.link H.! A.rel "stylesheet" H.! A.href "https://unpkg.com/normalize.css@8.0.1/normalize.css"
                H.link H.! A.rel "stylesheet" H.! A.href "/styles.css"
                H.script H.! A.src "https://unpkg.com/panzoom@9.4.0/dist/panzoom.min.js" $
                    pure ()
            H.body $ do
                -- ########################################################
                -- ##  header  ############################################
                -- ########################################################
                H.header $ do
                    H.h1 (H.toMarkup licRaw)
                    H.form H.! A.action "" $ do
                        H.input H.! A.name "license" H.! A.id "license" H.! A.value (H.toValue licRaw) H.! A.list "licenses"
                        H.datalist H.! A.id "licenses" $
                            mapM_ (\license -> H.option H.! A.value (fromString $ show license) $ pure ()) allLicenseNames
                        H.h4 "Sources"
                        H.ul $
                            mapM_ (\(Source source) -> H.li $ do
                                    H.input H.! A.type_ "checkbox" H.! A.name (fromString source) H.! A.value "on" H.! (if isSourceEnabled paramMap (Source source)
                                                                                                                        then A.checked "checked"
                                                                                                                        else mempty)
                                    H.label H.! A.for (fromString source) $ fromString source
                                ) allSources
                        H.h4 "Graph Options"
                        H.ul $ do
                            H.li $ do
                                H.input H.! A.type_ "checkbox" H.! A.name (H.toValue excludeStmts) H.! A.value "on" H.! (if getIsExcludeStmts paramMap
                                                                                                                         then A.checked "checked"
                                                                                                                         else mempty)
                                H.label H.! A.for (H.toValue excludeStmts) $ H.toMarkup excludeStmts
                        H.input H.! A.type_ "submit" H.! A.value "reload" H.! A.name "reload"
                -- ########################################################
                -- ##  svg  ###############################################
                -- ########################################################
                H.input H.! A.type_ "checkbox" H.! A.id "svgCheckbox"
                H.div H.! A.id "svgGraph" $ do
                    H.preEscapedToMarkup svg
                -- ########################################################
                -- ##  all  ###############################################
                -- ########################################################
                H.div H.! A.id "content" $ do
                    H.h2 "LicenseNames"
                    H.ul $ mapM_ (H.li . fromString . show) sameNames
                    H.h3 "LicenseName Hints"
                    H.ul $ mapM_ (H.li . fromString . show) otherNames
                    H.h2 "Facts"
                    H.ul $ mapM_ (\fact -> H.li $ do
                        let factId@(FactId ty hash) = getFactId fact
                        H.h3 $ do
                            H.a H.! A.href (H.toValue $ "./fact" </> ty </> hash) $ H.toMarkup (show factId)
                            -- ((H.toValue . ("./fact/"++)) n) $ H.toMarkup n) . show) cluster)) clusters
                        toMarkup fact
                        -- H.pre (H.toMarkup (let
                        --                     onerror _ _ = Just '_'
                        --                 in Enc.decodeUtf8With onerror (BL.toStrict (encodePretty fact))))
                        ) facts
                    H.h2 "LicenseNameSubgraph"
                    H.pre $
                        H.toMarkup (G.prettify lnsubgraph)
                H.script H.! A.src "/script.js" $
                    pure ()
                H.script "main();"

serve :: LicenseGraphM ()
serve = do
    licenseGraph <- MTL.get
    clusters <- getClusters

    infoLog "Start server on port 3000..."
    lift $ Temp.withSystemTempDirectory "ldbcollector-haskell" $ \tmpdir -> do
        putStrLn $ "tmpdir=" ++ tmpdir
        scottyOpts myOptions $ do
            get "/styles.css" $ raw (BL.fromStrict stylesheet)
            get "/script.js" $ raw (BL.fromStrict scriptJs)
            get "/" $ do
                params <- S.params
                page <- liftAndCatchIO $ mainPage params licenseGraph
                html (BT.renderHtml page)
            get "/svg/" $ do
                params <- S.params
                svg <- liftAndCatchIO $ svgPage params licenseGraph
                setHeader "Content-Type" "image/svg+xml"
                text svg
            get "/fact/:facttype/:facthash" $ do
                facttype <- fromString <$> param "facttype"
                facthash <- fromString <$> param "facthash"
                page <- liftAndCatchIO $ printFacts (FactId facttype facthash) licenseGraph
                html (BT.renderHtml page)

            get "/clusters" $ listPageAction clusters
            -- get "/svg/:lic" $ do
            --     lic <- fromString <$> param "lic"
            --     svg <- liftAndCatchIO $ genSvg tmpdir lic licenseGraph
            --     file svg
