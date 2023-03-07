{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE TemplateHaskell #-}
module Ldbcollector.Source.ChooseALicense
  ( ChooseALicense (..)
  ) where

import           Ldbcollector.Model    hiding (ByteString)

import           Data.List as L
import qualified Data.List.Split as Split
import qualified Data.Vector as V
import qualified Data.ByteString as B
import           Data.ByteString (ByteString)
import qualified Data.ByteString.Char8 as Char8

import qualified Data.Yaml as Y
import qualified Data.Yaml.Internal as Y
import qualified Text.Libyaml as YY
import           Data.Either (rights)

data CALData
  = CALData
  { _name :: Maybe String
  , _title :: Maybe String
  , _spdxId :: Maybe String 
  , _nickname :: Maybe String
  , _featured :: Maybe Bool
  , _hidden :: Maybe Bool
  , _description :: Maybe String
  , _how :: Maybe String
  , _permissions :: [String]
  , _conditions :: [String]
  , _limitations :: [String]
--   , _content :: ByteString
  } deriving (Show, Generic)
instance FromJSON CALData where
  parseJSON = withObject "CALData" $ \v -> CALData
    <$> v .:? "name"
    <*> v .:? "title"
    <*> v .:? "spdxid"
    <*> v .:? "nickname"
    <*> v .:? "featured"
    <*> v .:? "hidden"
    <*> v .:? "description"
    <*> v .:? "how"
    <*> v .:? "permissions" .!= []
    <*> v .:? "conditions" .!= []
    <*> v .:? "limitations" .!= []
instance ToJSON CALData


newtype ChooseALicense
    = ChooseALicense FilePath

applyTxt :: FilePath -> IO LicenseGraphTask
applyTxt txt = do
    putStrLn ("read " ++ txt)
    let fromFilename = takeBaseName (takeBaseName txt)
    contents <- readFile txt
    let contentLines = lines contents
    let parts = (map unlines . Split.splitOn ["---"]) contentLines

    case parts of 
        _:yaml:others -> do
            case Y.decodeEither' ((fromString . ("---\n"++)) yaml) of
                Left err -> do
                    putStrLn (show err)
                    return Noop
                Right calData -> 
                    return $
                        EdgeLeft (AddTs . V.fromList $
                           [ maybeToTask (Add . fromString) (_description calData)
                           , maybeToTask (Add . fromString) (_how calData)
                           ]) AppliesTo $
                        EdgeLeft (AddTs . V.fromList $
                           [ maybeToTask (Add . LicenseName . newLN . pack) (_name calData)
                           , maybeToTask (Add . LicenseName . newLN . pack) (_nickname calData)
                           , (Add . LicenseName . newLN . pack) fromFilename
                           ]) (Potentially Better) $
                        fromValue calData
                            (const $ (LicenseName . newNLN "choose-a-license" . pack) fromFilename)
                            (fmap (LicenseName . newNLN "spdx" . pack) . _spdxId)
        _ -> (return . Add . LicenseName . fromString) fromFilename

instance Source ChooseALicense where
    getTask (ChooseALicense dir) = do
        txts <- glob (dir </> "*.txt")
        AddTs . V.fromList <$> mapM applyTxt txts
