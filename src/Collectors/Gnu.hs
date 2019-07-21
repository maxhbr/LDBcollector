{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE TemplateHaskell #-}
module Collectors.Gnu
  ( loadGnuFacts
  , gnuLFC
  , loadGnuFactsFromByteString -- for Testing
  ) where

import qualified Prelude as P
import           MyPrelude hiding (ByteString)
import           Collectors.Common

import qualified Data.Vector as V
import           Text.XML.Hexml
import qualified Data.Map as Map
import qualified Data.ByteString as B
import           Data.ByteString (ByteString)
import qualified Data.ByteString.Char8 as Char8
import           Data.FileEmbed (embedDir)

import           Model.License

data GnuFact
  = GnuFact
  { isGnuFree :: Bool
  , isGnuGplCompatible :: Bool
  , gnuHeader :: !ByteString
  , gnuBody :: !ByteString
  } deriving (Show, Generic)
instance ToJSON GnuFact where
  toJSON (GnuFact isFree isGCompatible a b) = object [ "header" .= Char8.unpack a
                                                     , "body" .= Char8.unpack b
                                                     , "isFree" .= isFree
                                                     , "isGPLComptible" .= isGCompatible
                                                     ]
gnuLFC :: LicenseFactClassifier
gnuLFC = LFC "gnu.org"
instance LFRaw GnuFact where
  getLicenseFactClassifier _ = gnuLFC
  getImpliedNames _          = NoCLSR -- TODO: extract names!
  getImpliedJudgement gf = SLSR (getLicenseFactClassifier gf) $
                           if isGnuFree gf
                           then PositiveJudgement "Is Gnu free"
                           else NegativeJudgement "Is not Gnu free"

reduceListOfChildren :: Bool -> Bool -> [Node]  -> Facts
reduceListOfChildren isFree isGCompatible (n1:(n2:ns)) = let
    r1 = trace (show n1) $ render n1
    r2 = trace (show n2) $ render n2
  in (LicenseFact Nothing (GnuFact isFree isGCompatible r1 r2)) `V.cons` (reduceListOfChildren isFree isGCompatible ns)
reduceListOfChildren _ _ [n0]                          = undefined
reduceListOfChildren _ _ _                             = V.empty

loadGnuFactsFromByteString :: Bool -> Bool -> ByteString -> Either ByteString Facts
loadGnuFactsFromByteString isFree isGCompatible content = let
    splitNodes :: Node -> [Node]
    splitNodes dl = children $ children dl !! 0
    nodeToFacts :: Node -> Facts
    nodeToFacts = reduceListOfChildren isFree isGCompatible . splitNodes
  in case (parse content :: Either ByteString Node) of
    Left err -> Left err
    Right n  -> Right (nodeToFacts n)

loadGnuFactsFromFile :: Bool -> Bool -> FilePath -> IO Facts
loadGnuFactsFromFile isFree isGCompatible htmlFile = do
  content <- B.readFile htmlFile
  case loadGnuFactsFromByteString isFree isGCompatible content of
    Left err -> do
          Char8.putStrLn err
          return V.empty
    Right fs -> return fs

gnuFolder :: Map FilePath ByteString
gnuFolder = Map.fromList $(embedDir "data/gnu.org/")

loadGnuFacts :: IO Facts
loadGnuFacts = let
    fs1E = loadGnuFactsFromByteString True True (gnuFolder Map.! "GPL-Compatible_Free_Software_Licenses.html")
    fs2E = loadGnuFactsFromByteString True False (gnuFolder Map.! "GPL-Incompatible_Free_Software_Licenses.html")
    fs3E = loadGnuFactsFromByteString False False (gnuFolder Map.! "Nonfree_Software_Licenses.html")
    handleEither :: Either ByteString Facts -> IO Facts
    handleEither res = case res of
      Left err -> do
            Char8.putStrLn err
            return V.empty
      Right fs -> return fs
  in do
    logThatFactsAreLoadedFrom "Gnu"
    fs1 <- handleEither fs1E
    fs2 <- handleEither fs2E
    fs3 <- handleEither fs3E
    return $ V.concat [fs1, fs2, fs3]
