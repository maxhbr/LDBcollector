{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE OverloadedStrings #-}

module Main where

import Control.Concurrent (getNumCapabilities)
import Control.Concurrent.Async.Pool (mapConcurrently, withTaskGroup)
import Control.Monad.State qualified as MTL
import Data.Monoid (mconcat)
import Data.Text qualified as T
import Data.Text.Lazy qualified as TL
import Data.Vector qualified as V
import Ldbcollector.Model
import Ldbcollector.Server
import Ldbcollector.Sink.GraphViz
import Ldbcollector.Sink.JSON
import Ldbcollector.Sink.Metrics
import Ldbcollector.Sink.NameClustersCSV
import Ldbcollector.Source
import Main.Utf8 (withUtf8)
import Options.Applicative
import System.Directory (getCurrentDirectory)
import System.Environment (getArgs)
import Prelude hiding (div, head, id)

data Command
  = Serve
  | Generate Text
  | Default Text
  | Write [String] Text
  | WriteNS String Text
  deriving (Show)

writeFilesByName :: FilePath -> LicenseName -> LicenseGraphM ()
writeFilesByName outDir lic = do
  let dot =
        outDir
          </> ( case lic of
                  LicenseName (Just ns) name -> T.unpack ns </> T.unpack name
                  LicenseName Nothing name -> T.unpack name
              )
          <.> "dot"
      json = dot -<.> "json"
      html = dot -<.> "html"
  lift $ createDirectoryIfMissing True (dropFileName dot)
  infoLog $ "generate " ++ dot ++ " ..."
  focus mempty (V.singleton (LGName lic)) $
    \(needleNames, sameNames, otherNames, _statements) -> do
      writeJSON json
      writeGraphViz needleNames sameNames otherNames dot
      writeSingleHtml html ((TL.fromStrict . licenseNameToText) lic) (needleNames, sameNames, otherNames)
  infoLog "... done"

writeSvgByNS :: FilePath -> Vector LicenseName -> Text -> LicenseGraphM ()
writeSvgByNS outDir filteredLicenses selectedNS = do
  timedLGM ("writing " ++ show (V.length filteredLicenses) ++ " licenses of NS=" ++ T.unpack selectedNS) $ do
    numCaps <- lift $ getNumCapabilities
    graph <- MTL.get
    lift $ withTaskGroup (max 1 (numCaps - 3)) $ \group -> do
      _ <- mapConcurrently group (runLicenseGraphM' graph . writeFilesByName outDir) (V.toList filteredLicenses)
      return ()

curation :: Vector CurationItem
curation =
  let alternativeLNsCuration =
        V.fromList $
          map
            (\(main, alternatives) -> CurationItem (LN main `AlternativeLNs` map LN alternatives) [])
            [ ("GPL-1.0-only", ["GPL-1.0", "GPL1.0", "GPL1", "GNU General Public License Version 1"]),
              ("GPL-2.0-only", ["GPL-2.0", "GPL2.0", "GPL2", "GPL (v2)", "GNU General Public License Version 2"]),
              ("GPL-3.0-only", ["GPL-3.0", "GPL3.0", "GPL3", "GPL (v3)", "GNU General Public License Version 3"]),
              ("LGPL-2.0-only", ["GNU Library General Public License Version 2"]),
              ("LGPL-2.1-only", ["LGPL-2.1", "LGPL2.1", "LGPL2.1", "LGPL (v2.1)", "GNU Lesser General Public License Version 2.1"]),
              ("LGPL-3.0-only", ["LGPL-3.0", "LGPL-3", "LGPL3.0", "LGPL3", "LGPL (v3.0)", "LGPL (v3)", "GNU Lesser General Public License Version 3"]),
              ("AGPL-1.0-only", ["AGPL-1.0", "Affero General Public License (v. 1)", "Affero General Public License 1.0"]),
              ("AGPL-3.0-only", ["AGPL-3.0", "AGPL3.0", "AGPL3", "AGPL (v3)", "Affero General Public License 3.0", "GNU AFFERO GENERAL PUBLIC LICENSE Version 3", "GNU Affero General Public License (AGPL-3.0) (v. 3.0)"]),
              ("AGPL-3.0-or-later", ["AGPL-3.0+", "AGPL3.0+", "AGPL3+", "AGPL (v3 or later)", "Affero General Public License 3.0 or later"]),
              ("GPL-1.0-or-later", ["GPL-1.0+", "GPL1.0+", "GPL1+"]),
              ("GPL-2.0-or-later", ["GPL-2.0+", "GPL2.0+", "GPL2+", "GPL (v2 or later)"]),
              ("GPL-3.0-or-later", ["GPL-3.0+", "GPL3.0+", "GPL3+", "GPL (v3 or later)"]),
              ("LGPL-2.1-or-later", ["LGPL-2.1+", "LGPL2.1+", "LGPL2.1+", "LGPL (v2.1 or later)"]),
              ("LGPL-3.0-or-later", ["LGPL-3.0+", "LGPL-3+", "LGPL3.0+", "LGPL3", "LGPL (v3.0)", "LGPL (v3 or later)"]),
              ("BSL-1.0", ["BSL (v1.0)"]),
              ("Zlib", ["zlib/libpng"]),
              ("Apache-1.0", ["Apache (v1.0)", "Apache Software License 1.0", "ASL 1.0", "Apache Software License, Version 1.0"]),
              ("Apache-1.1", ["Apache (v1.1)", "Apache Software License 1.1", "ASL 1.1", "Apache Software License, Version 1.1"]),
              ("Apache-2.0", ["Apache (v2.0)", "Apache Software License 2.0", "ASL 2.0", "Apache License, Version 2.0", "ALv2"]),
              ("BSL-1.0", ["BSL (v1)"]),
              ("BSD-2-Clause", ["BSD (2 clause)", "BSD License (two clause)"]),
              ("BSD-3-Clause", ["BSD (3 clause)", "BSD License (no advertising)"]),
              ("BSD-4-Clause", ["BSD License (original)"]),
              ("MIT", ["MIT license (also X11)", "The MIT License"]),
              ("Sleepycat", ["Berkeley Database License", "Sleepycat Software Product License", "Sleepycat License"]),
              ("Artistic-1.0", ["Artistic 1.0 (original)"]),
              ("ClArtistic", ["Artistic (clarified)"]),
              ("Artistic-2.0", ["Artistic 2.0", "Artistic License (v. 2.0)"]),
              ("UPL-1.0", ["UPL"]),
              ("LiLiQ-P-1.1", ["LiLiQ-P"]),
              ("LiLiQ-R-1.1", ["LiLiQ-R"]),
              ("LiLiQ-Rplus-1.1", ["LiLiQ-R+"])
            ]
   in alternativeLNsCuration

executeCommand :: Command -> LicenseGraphM ()
executeCommand = \case
  Serve -> serve
  Generate outDir -> do
    writeNameClustersCsv (T.unpack outDir </> "license-name-clusters.csv")
    writeJSON (T.unpack outDir </> "yacp.json")
  Default outDir -> do
    executeCommand (Generate outDir)
    executeCommand (WriteNS "spdx" outDir)
  Write names outDir -> mapM_ (writeFilesByName (T.unpack outDir) . fromString) names
  WriteNS ns outDir -> do
    allLicenseNames <- MTL.gets getLicenseGraphLicenseNames
    let filteredLicenses =
          V.filter
            ( \case
                LicenseName (Just licNS) name -> licNS == fromString ns && not ("LicenseRef-" `isInfixOf` T.unpack name)
                _ -> False
            )
            allLicenseNames
    writeSvgByNS (T.unpack outDir) filteredLicenses (fromString ns)
    writeOutputLicensesJSON (T.unpack outDir) (fromString ns)

optDir :: Parser Text
optDir = strOption $ long "output-dir" <> short 'o' <> metavar "DIR" <> value "_generatedV2" <> help "Output directory for generated files"

serveParser :: Parser Command
serveParser = pure Serve

generateParser :: Parser Command
generateParser = Generate <$> optDir

defaultParser :: Parser Command
defaultParser = Default <$> optDir

writeParser :: Parser Command
writeParser =
  fmap (\(names, mOutDir) -> Write names (fromMaybe "_generatedV2" mOutDir)) $
    (,) <$> many (argument str (metavar "NAME")) <*> optional optDir

writeNSParser :: Parser Command
writeNSParser =
  fmap (\(ns, mOutDir) -> WriteNS ns (fromMaybe "_generatedV2" mOutDir)) $
    (,) <$> argument str (metavar "NAMESPACE") <*> optional optDir

cmdParser :: Parser Command
cmdParser =
  subparser
    ( command "serve" (info serveParser (progDesc "Start the web server"))
        <> command "generate" (info generateParser (progDesc "Generate name clusters and JSON"))
        <> command "default" (info defaultParser (progDesc "Generate and write SPDX licenses"))
        <> command "write" (info writeParser (progDesc "Write files for specific license names"))
        <> command "writeNS" (info writeNSParser (progDesc "Write files for licenses in namespace"))
    )

mainParser :: ParserInfo Command
mainParser =
  info
    (versionOption <*> helper <*> cmdParser)
    ( fullDesc
        <> progDesc "License database collector and generator"
        <> header "ldbcollector - Collect and generate license information"
    )
  where
    versionOption :: Parser (a -> a)
    versionOption =
      infoOption
        "ldbcollector 0.1.0.0"
        (long "version" <> short 'v' <> help "Show version")

main' :: Command -> IO ()
main' cmd = do
  (_, licenseGraph) <- runLicenseGraphM $ do
    timedLGM "warmup" $ do
      timedLGM "applySources" $
        applySources curation
      writeMetrics
    executeCommand cmd
  return ()

main :: IO ()
main = withUtf8 $ do
  cwd <- getCurrentDirectory
  putStrLn $ "cwd: " ++ cwd
  cmd <- execParser mainParser
  setupLogger True
  main' cmd
