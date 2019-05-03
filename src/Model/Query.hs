{-# LANGUAGE Rank2Types #-}
module Model.Query
  ( queryLicense
  , queryByteString
  ) where

import qualified Prelude as P
import           MyPrelude

import           Data.Aeson.Lens
import           Control.Lens
import           Data.ByteString.Lazy (ByteString)

import Model.License

queryLicense :: LicenseFactClassifier -> Traversal' Value o -> License -> Maybe o
queryLicense lfc qry l = let
    k = tShow lfc
  in getFactJSON l lfc >>= queryByteString (key k . qry)

queryByteString :: Traversal' ByteString o -> ByteString -> Maybe o
queryByteString qry jsonString = jsonString ^? qry
