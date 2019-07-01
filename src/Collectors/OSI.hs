{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE ScopedTypeVariables #-}
module Collectors.OSI
  ( loadOSIFacts
  , osiLFC
  ) where

import qualified Prelude as P
import           MyPrelude hiding (id)
import           Collectors.Common

import           Control.Monad.Trans.Except (runExceptT)
import           Control.Exception (try)
import           Network.Protocol.OpenSource.License
import qualified Data.Text as T
import qualified Data.Vector as V
import           Network.HTTP.Client (HttpException (..))

import           Model.License

osiLFC :: LicenseFactClassifier
osiLFC = LFC "OpenSourceInitiative"
instance LFRaw OSILicense where
  getLicenseFactClassifier _                       = osiLFC
  getImpliedNames OSILicense{ olId = i
                            , olName = n
                            , olIdentifiers = is
                            , olOther_names = os } = CLSR $ map T.unpack $ [i,n] ++ map oiIdentifier is ++ map oonName os
  getImpliedURLs OSILicense{ olLinks = links }     = CLSR $ map (\l -> (Just . T.unpack $ olNote l, T.unpack $ olUrl l)) links
  getImpliedJudgement osil@OSILicense{ olOther_names = os } = case unlines . nub . map T.unpack . catMaybes $ map oonNote os of
    ""       -> NoSLSR
    comments -> SLSR (getLicenseFactClassifier osil) (NeutralJudgement comments)

loadOSIFacts :: IO Facts
loadOSIFacts = let
  loadOSIFacts' :: IO Facts
  loadOSIFacts' = do
    logThatFactsAreLoadedFrom "OSI License List"
    els <- runExceptT allLicenses
    case els of
            Right ls -> return . V.fromList $ map (LicenseFact (Just "https://opensource.org/licenses/")) ls
            Left err -> do
              hPutStrLn stderr err
              return V.empty
  in do
    (res :: Either HttpException Facts) <- try loadOSIFacts'
    case res of
      Right ls -> return ls
      Left err -> do
        hPutStrLn stderr (show err)
        return V.empty
