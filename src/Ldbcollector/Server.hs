{-# LANGUAGE OverloadedStrings #-}
module Ldbcollector.Server
    ( serve
    ) where

import           Ldbcollector.Model

import qualified Data.Vector                        as V

import qualified Control.Monad.State                as MTL
import           Data.Monoid                        (mconcat)
import           Data.Text.Lazy                     as T
import qualified System.IO.Temp                     as Temp
import qualified Text.Blaze.Html.Renderer.Text      as BT
import qualified Text.Blaze.Html4.Strict            as B
import qualified Text.Blaze.Html4.Strict.Attributes as B hiding (span, title)
import           Web.Scotty

import           Ldbcollector.Model
import           Ldbcollector.Sink.GraphViz
import           Ldbcollector.Source

serve :: LicenseGraphM ()
serve = do
    licenseGraph <- MTL.get
    let names = getLicenseGraphLicenseNames licenseGraph
    clusters <- getClusters

    lift $ Temp.withSystemTempDirectory "ldbcollector-haskell" $ \tmpdir -> do
        putStrLn $ "tmpdir=" ++ tmpdir
        scotty 3000 $ do

            get "/" $ do
                let page = B.html $ do
                        B.head $ B.title "ldbcollector-haskell"
                        B.body $ do

                            B.ul $ mapM_ (\cluster ->
                                B.li (B.ul $ mapM_ (B.li . (\n -> B.a B.! B.href ((B.toValue . ("./svg/"++)) n) $ B.toMarkup n) . show) cluster)) clusters


                            -- B.ul $ V.mapM_ (B.li . (\n -> B.a B.! B.href ((B.toValue . ("./svg/"++)) n) $ B.toMarkup $ n) . show) names
                html (BT.renderHtml page)

            get "/svg/:lic" $ do
                licRaw <- param "lic"
                let lic = fromString licRaw :: LicenseName
                let dot = tmpdir </> show lic <.> "dot"
                let svg = dot <.> "Svg"
                liftAndCatchIO $ do
                    _ <- runLicenseGraphM' licenseGraph $
                        focus ((V.singleton . LGName) lic) $
                            writeGraphViz dot
                    return ()
                file svg