{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE OverloadedStrings #-}
module Collectors.OSI
  ( loadOSIFacts
  ) where

import qualified Prelude as P
import           MyPrelude hiding (id)
import           Collectors.Common

import           Control.Monad.Trans.Except (runExceptT)
import           Network.Protocol.OpenSource.License
import qualified Data.Text as T
import qualified Data.Vector as V

import           Model.License

instance LFRaw OSILicense where
  getLicenseFactClassifier _                       = LFC ["OpenSourceInitiative", "OSILicense"]
  getImpliedNames OSILicense{ olId = i
                            , olName = n
                            , olIdentifiers = is
                            , olOther_names = os } = CLSR $ map T.unpack $ [i,n] ++ (map oiIdentifier is) ++ (map oonName os)
  getImpliedURLs OSILicense{ olLinks = links }     = CLSR $ map (\l -> (T.unpack $ olNote l, T.unpack $ olUrl l)) links

loadOSIFacts :: IO Facts
loadOSIFacts = do
  logThatFactsAreLoadedFrom "OSI License List"
  els <- runExceptT allLicenses
  case els of
    Right ls -> return . V.fromList $ map (LicenseFact "https://opensource.org/licenses/") ls
    Left err -> do
      hPutStrLn stderr err
      return V.empty
