module Collectors.Common
    where

import qualified Prelude as P
import           MyPrelude

import qualified Data.Vector as V

import           Model.License

logThatFactsAreLoadedFrom :: String -> IO ()
logThatFactsAreLoadedFrom name = hPutStrLn stderr $ "## Load facts from: " ++ name

logThatFactsWithNumberAreLoadedFrom :: String -> IO Facts -> IO Facts
logThatFactsWithNumberAreLoadedFrom name getFacts = do
  hPutStrLn stderr $ "## Load facts from: " ++ name
  facts <- getFacts
  hPutStrLn stderr $ "### " ++ name ++ " found " ++ show (V.length facts) ++ " facts"
  return facts

logThatOneHasFoundFact :: String -> LicenseFact -> IO ()
logThatOneHasFoundFact name f = hPutStrLn stderr $ "### " ++ name ++ " has found a fact for: " ++ show (getImpliedNames f)

logThatOneHasFoundFacts :: String -> [LicenseFact] -> IO ()
logThatOneHasFoundFacts name fs = hPutStrLn stderr $ "### " ++ name ++ " has found a fact for: " ++ show (map getImpliedNames fs)

logThatFileContainedFact :: FilePath -> LicenseFact -> IO ()
logThatFileContainedFact file f = hPutStrLn stderr $ "### the file " ++ file ++ " contained fact for: " ++ show (getImpliedNames f)

--------------------------------------------------------------------------------
--
data CollectorUpdateMethod
  = ScriptCollectorUpdateMethod FilePath
  | ManualCollectorUpdateMethod String -- description
  | DirectPullUpdateMethod String -- description
  deriving (Eq, Show)
class (LicenseFactClassifiable a) => Collector a where
  loadFacts :: a -> IO Facts
  -- metadata
  getCollectorUpdateMethod :: a -> CollectorUpdateMethod
  getCollectorVersion :: a -> LicenseFactVersion
