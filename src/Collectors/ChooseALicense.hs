{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE OverloadedStrings #-}
module Collectors.ChooseALicense
  ( loadChooseALicenseFacts
  ) where

import Prelude hiding (id)

import           System.FilePath
import           System.Directory
import           Data.List
import qualified Data.Text as T
import qualified Data.Vector as V
import           Debug.Trace (trace)
import qualified Data.ByteString as B
import           Data.ByteString (ByteString)
import qualified Data.ByteString.Char8 as Char8

import           Data.Aeson
import           GHC.Generics

import           Model.License

data CALFactRaw
  = CALFactRaw
  { name :: LicenseShortname
  , title :: Maybe String
  , spdxId :: Maybe LicenseShortname
  , content :: ByteString
  } deriving (Show, Generic)
instance ToJSON ByteString where
  toJSON = toJSON . Char8.unpack
instance ToJSON CALFactRaw
instance LFRaw CALFactRaw where
  getImpliedShortnames (CALFactRaw sn _ sid _) = [sn] ++ (case sid of
                                                            Just v  -> [v]
                                                            Nothing -> [])
  getType _                                    = "CALFact"

loadCalFactFromFile :: FilePath -> FilePath -> IO LicenseFact
loadCalFactFromFile calFolder calFile = let
    fileWithPath = calFolder </> calFile
    name = dropExtension calFile
  in do
    cnt <- B.readFile fileWithPath
    let sCnt = Char8.unpack cnt
        ls = lines sCnt
        getValueFor key = let
            prefix = key ++ ": "
          in stripPrefix prefix ((filter (prefix `isPrefixOf`) ls) !! 0)
        t = getValueFor "title"
        sid = getValueFor "spdx-id"
    return (mkLicenseFact "choosealicense.com" (CALFactRaw name t sid cnt))

loadChooseALicenseFacts :: FilePath -> IO Facts
loadChooseALicenseFacts calFolder = do
  files <- getDirectoryContents calFolder
  let cals = filter ("txt" `isSuffixOf`) files
  facts <- mapM (loadCalFactFromFile calFolder) cals
  return (V.fromList facts)
