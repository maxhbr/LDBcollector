{-# LANGUAGE OverloadedStrings #-}
module Main where

import qualified Data.Vector                        as V
import           Prelude                            hiding (div, head, id)

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


serve :: LicenseGraph -> IO ()
serve licenseGraph = Temp.withSystemTempDirectory "ldbcollector-haskell" $ \tmpdir -> do
    putStrLn $ "tmpdir=" ++ tmpdir
    scotty 3000 $ do
        get "/" $ do
            let names = getLicenseGraphLicenseNames licenseGraph

            let page = B.html $ do
                    B.head $ B.title "ldbcollector-haskell"
                    B.body $ do
                        B.ul $ V.mapM_ (B.li . (\n -> B.a B.! B.href ((B.toValue . ("./"++)) n) $ B.toMarkup $ n) . show) names


            html (BT.renderHtml page)
        get "/:lic" $ do
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

main :: IO ()
main = do
    (_, licenseGraph) <- runLicenseGraphM $ do
        applySources
        -- let lns = map (LicenseName . newLN)
        --         [ "BSD-3-Clause"
        --         ]
        -- let nlns = map (LicenseName . uncurry newNLN)
        --         [ ("SPDX", "Apache-2.0")
        --         , ("scancode", "sleepycat")
        --         ]
        -- focus (V.fromList (lns ++ nlns)) $
        --     writeGraphViz "_out/focused.graph.dot"

    serve licenseGraph
    return ()
