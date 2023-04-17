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
curation = V.fromList $
  map (\(main,alternatives) -> CurationItem (LN main `AlternativeLNs` map LN alternatives) [])
    [ ( "GPL-1.0-only", [ "GPL-1.0", "GPL1.0", "GPL1", "GNU General Public License Version 1" ])
    , ( "GPL-2.0-only", [ "GPL-2.0", "GPL2.0", "GPL2", "GPL (v2)", "GNU General Public License Version 2" ])
    , ( "GPL-3.0-only", [ "GPL-3.0", "GPL3.0", "GPL3", "GPL (v3)", "GNU General Public License Version 3" ])
    , ("LGPL-2.0-only", [ "GNU Library General Public License Version 2" ])
    , ( "LGPL-2.1-only", [ "LGPL-2.1", "LGPL2.1", "LGPL2.1", "LGPL (v2.1)", "GNU Lesser General Public License Version 2.1" ])
    , ( "LGPL-3.0-only", [ "LGPL-3.0", "LGPL-3", "LGPL3.0", "LGPL3", "LGPL (v3.0)", "LGPL (v3)", "GNU Lesser General Public License Version 3" ])
    , ( "AGPL-1.0-only", [ "AGPL-1.0", "Affero General Public License (v. 1)", "Affero General Public License 1.0" ])
    , ( "AGPL-3.0-only", [ "AGPL-3.0", "AGPL3.0", "AGPL3", "AGPL (v3)", "Affero General Public License 3.0", "GNU AFFERO GENERAL PUBLIC LICENSE Version 3", "GNU Affero General Public License (AGPL-3.0) (v. 3.0)" ])
    , ( "AGPL-3.0-or-later", [ "AGPL-3.0+", "AGPL3.0+", "AGPL3+", "AGPL (v3 or later)", "Affero General Public License 3.0 or later" ])
    , ("GPL-1.0-or-later", [ "GPL-1.0+", "GPL1.0+", "GPL1+" ])
    , ( "GPL-2.0-or-later", [ "GPL-2.0+", "GPL2.0+", "GPL2+", "GPL (v2 or later)" ])
    , ( "GPL-3.0-or-later", [ "GPL-3.0+", "GPL3.0+", "GPL3+", "GPL (v3 or later)" ])
    , ( "LGPL-2.1-or-later", [ "LGPL-2.1+", "LGPL2.1+", "LGPL2.1+", "LGPL (v2.1 or later)" ])
    , ( "LGPL-3.0-or-later", [ "LGPL-3.0+", "LGPL-3+", "LGPL3.0+", "LGPL3", "LGPL (v3.0)", "LGPL (v3 or later)" ])
    , ("BSL-1.0", [ "BSL (v1.0)" ])
    , ("Zlib", [ "zlib/libpng" ])
    , ( "Apache-1.0", [ "Apache (v1.0)", "Apache Software License 1.0", "ASL 1.0", "Apache Software License, Version 1.0" ])
    , ( "Apache-1.1", [ "Apache (v1.1)", "Apache Software License 1.1", "ASL 1.1", "Apache Software License, Version 1.1" ])
    , ( "Apache-2.0", [ "Apache (v2.0)", "Apache Software License 2.0", "ASL 2.0", "Apache License, Version 2.0", "ALv2" ])
    , ("BSL-1.0", [ "BSL (v1)" ])
    , ("BSD-2-Clause", [ "BSD (2 clause)", "BSD License (two clause)" ])
    , ("BSD-3-Clause", [ "BSD (3 clause)", "BSD License (no advertising)" ])
    , ("BSD-4-Clause", [ "BSD License (original)" ])
    , ("MIT", [ "MIT license (also X11)", "The MIT License" ])
    , ( "Sleepycat", [ "Berkeley Database License", "Sleepycat Software Product License", "Sleepycat License" ])
    , ("Artistic-1.0", [ "Artistic 1.0 (original)" ])
    , ("ClArtistic", [ "Artistic (clarified)" ])
    , ("Artistic-2.0", [ "Artistic 2.0", "Artistic License (v. 2.0)" ])
            -- link to missing versions in OpenChainPolicyTemplate
    , ("UPL-1.0", [ "UPL" ])
    , ("LiLiQ-P-1.1", [ "LiLiQ-P" ])
    , ("LiLiQ-R-1.1", [ "LiLiQ-R" ])
    , ("LiLiQ-Rplus-1.1", [ "LiLiQ-R+" ])
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
