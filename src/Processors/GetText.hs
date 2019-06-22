{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE LambdaCase #-}
module Processors.GetText
  ( getTextOfLicense
  ) where

import qualified Prelude as P
import           MyPrelude

import qualified Data.Aeson.Types as A
import qualified Data.Aeson.Lens as AL
import qualified Data.Text as T
  
import           Debug.Trace (trace)

import           Model.Fact
import           Model.License
import           Model.Query

getTextOfLicense :: License -> Text
getTextOfLicense lic = let
    fromScancode = queryLicense (LFC ["ScancodeData"]) (AL.key "text" . AL._String) lic
  in case fromScancode of
    Just text -> text
    Nothing   -> ""
