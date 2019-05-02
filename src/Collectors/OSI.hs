{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE OverloadedStrings #-}
module Collectors.OSI
  ( loadOSIFacts
  ) where

import           System.IO (hPutStrLn, stderr)
import           Control.Monad.Trans.Except (runExceptT)
import           Network.Protocol.OpenSource.License
import qualified Data.Text as T
import qualified Data.Vector as V

import           Model.License

instance LFRaw OSILicense where
  getImpliedNames OSILicense{ olId = i
                            , olName = n
                            , olIdentifiers = is
                            , olOther_names = os } = map T.unpack $ [i,n] ++ (map oiIdentifier is) ++ (map oonName os)
  getType _                                        = "OSILicense"

loadOSIFacts = do
  els <- runExceptT $ allLicenses
  case els of
    Right ls -> return . V.fromList $ map (mkLicenseFact "OpenSourceInitiative") ls
    Left err -> do
      hPutStrLn stderr err
      return V.empty
