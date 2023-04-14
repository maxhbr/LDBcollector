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
import           Ldbcollector.Source

writeSvgByName :: FilePath -> LicenseName -> LicenseGraphM ()
writeSvgByName outDir lic = do
    let dot =  outDir </> (case lic of
                                LicenseName (Just ns) name -> T.unpack ns </> T.unpack name
                                LicenseName Nothing name   -> T.unpack name
                            ) <.> "dot"
    lift $ createDirectoryIfMissing True (dropFileName dot)
    infoLog $ "generate " ++ dot ++ " ..."
    focus mempty (V.singleton (LGName lic)) $
            \(needleNames, sameNames, otherNames, _statements) -> do
                writeGraphViz needleNames sameNames otherNames dot
    infoLog "... done"

genSvgByNS :: FilePath -> Text -> LicenseGraphM ()
genSvgByNS outDir selectedNS = do
    allLicenseNames <- MTL.gets getLicenseGraphLicenseNames
    let filteredLicenses = V.filter (\case
                                       LicenseName (Just ns) name -> ns == selectedNS && not ("LicenseRef-" `isInfixOf` T.unpack name)
                                       _ -> False) allLicenseNames
    V.mapM_ (writeSvgByName outDir) filteredLicenses


main :: IO ()
main = do
    args <- getArgs
    setupLogger
    (_, licenseGraph) <- runLicenseGraphM $ do
        applySources
        writeMetrics
        case args of
            "write":names -> mapM_ (genSvgByNS "_out" . fromString) names
            ["writeNS", ns] -> genSvgByNS "_out" (fromString ns)
            _ -> serve
    return ()
