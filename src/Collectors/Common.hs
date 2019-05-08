module Collectors.Common
    where

import qualified Prelude as P
import           MyPrelude
import           Model.License

logThatFactsAreLoadedFrom :: String -> IO ()
logThatFactsAreLoadedFrom name = hPutStrLn stderr $ "## Load facts from: " ++ name

logThatOneHasFoundFact :: String -> LicenseFact -> IO ()
logThatOneHasFoundFact name f = hPutStrLn stderr $ "### " ++ name ++ " has found a fact for: " ++ show (getImpliedNames f)

logThatFileContainedFact :: FilePath -> LicenseFact -> IO ()
logThatFileContainedFact file f = hPutStrLn stderr $ "### the file " ++ file ++ " contained fact for: " ++ show (getImpliedNames f)
