{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE OverloadedStrings #-}
module Collectors.Gnu
  ( loadGnuFacts
  , loadGnuFactsFromByteString -- for Testing
  ) where

import qualified Prelude as P
import           MyPrelude hiding (ByteString)
import           Collectors.Common

import qualified Data.Vector as V
import           Text.XML.Hexml
import qualified Data.ByteString as B
import           Data.ByteString (ByteString)
import qualified Data.ByteString.Char8 as Char8

import           Model.License

data GnuFact
  = GnuFact !ByteString !ByteString -- TODO: parse content and pack it into more useful data structures
  deriving (Show, Generic)
instance ToJSON GnuFact where
  toJSON (GnuFact a b) = object [ "header" .= (Char8.unpack a), "body" .= (Char8.unpack b) ]
instance LFRaw GnuFact where
  getLicenseFactClassifier _ = LFC ["gnu.org", "GnuFact"]
  getImpliedNames _          = [] -- TODO: extract names!

reduceListOfChildren :: [Node]  -> Facts
reduceListOfChildren (n1:(n2:ns)) = let
    r1 = trace (show n1) $ render n1
    r2 = trace (show n2) $ render n2
  in (LicenseFact "" (GnuFact r1 r2)) `V.cons` (reduceListOfChildren ns)
reduceListOfChildren [n0]         = undefined
reduceListOfChildren _            = V.empty

loadGnuFactsFromByteString :: ByteString -> Either ByteString Facts
loadGnuFactsFromByteString content = let
    splitNodes :: Node -> [Node]
    splitNodes dl = children $ children dl !! 0
    nodeToFacts :: Node -> Facts
    nodeToFacts = reduceListOfChildren . splitNodes
  in case (parse content :: Either ByteString Node) of
    Left err -> Left err
    Right n  -> Right (nodeToFacts n)

loadGnuFactsFromFile :: FilePath -> IO Facts
loadGnuFactsFromFile htmlFile = do
  content <- B.readFile htmlFile
  case (loadGnuFactsFromByteString content) of
    Left err -> do
          Char8.putStrLn err
          return V.empty
    Right fs -> return fs

loadGnuFacts :: FilePath -> IO Facts
loadGnuFacts gnuDir = do
  fs1 <- loadGnuFactsFromFile (gnuDir </> "GPL-Compatible_Free_Software_Licenses.html")
  fs2 <- loadGnuFactsFromFile (gnuDir </> "GPL-Incompatible_Free_Software_Licenses.html")
  fs3 <- loadGnuFactsFromFile (gnuDir </> "Nonfree_Software_Licenses.html")
  return $ V.concat [fs1, fs2, fs3]
