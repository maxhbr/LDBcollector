{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE LambdaCase #-}
module Main where

import qualified Data.Vector                as V
import           Prelude                    hiding (div, head, id)

import qualified Control.Monad.State        as MTL
import           Data.Monoid                (mconcat)
import qualified Data.Text as T
import           System.Environment (getArgs)

import           Ldbcollector.Model
import           Ldbcollector.Server
import           Ldbcollector.Sink.GraphViz
import           Ldbcollector.Sink.Metrics
import           Ldbcollector.Sink.JSON
import           Ldbcollector.Source

writeSvgByName :: FilePath -> LicenseName -> LicenseGraphM ()
writeSvgByName outDir lic = do
    let dot =  outDir </> (case lic of
                                LicenseName (Just ns) name -> T.unpack ns </> T.unpack name
                                LicenseName Nothing name   -> T.unpack name
                            ) <.> "dot"
        json = dot -<.> "json"
    lift $ createDirectoryIfMissing True (dropFileName dot)
    infoLog $ "generate " ++ dot ++ " ..."
    focus mempty (V.singleton (LGName lic)) $
            \(needleNames, sameNames, otherNames, _statements) -> do
                writeJSON json
                writeGraphViz needleNames sameNames otherNames dot
    infoLog "... done"

writeSvgByNS :: FilePath -> Text -> LicenseGraphM ()
writeSvgByNS outDir selectedNS = do
    allLicenseNames <- MTL.gets getLicenseGraphLicenseNames
    let filteredLicenses = V.filter (\case
                                       LicenseName (Just ns) name -> ns == selectedNS && not ("LicenseRef-" `isInfixOf` T.unpack name)
                                       _ -> False) allLicenseNames
    V.mapM_ (writeSvgByName outDir) filteredLicenses


curation :: Vector CurationItem
curation = V.fromList
  [ CurationItem (LN "spdx:NullBSD" `AlternativeLNs` [LN "BSD0", LN "0BSD"]) []
  ]

main :: IO ()
main = do
    args <- getArgs
    setupLogger
    (_, licenseGraph) <- runLicenseGraphM $ do
        applySources curation
        writeMetrics
        case args of
            "write":names -> mapM_ (writeSvgByName "_out" . fromString) names
            ["writeNS", ns] -> writeSvgByNS "_out" (fromString ns)
            _ -> serve
    return ()
