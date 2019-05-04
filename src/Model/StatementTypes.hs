{-# LANGUAGE OverloadedStrings #-}
module Model.StatementTypes
  where

import           Data.Aeson
import           Data.Text (Text)

import Model.Fact

data IsPermissiveStatement
  = IsPermissiveStatement Bool
instance FSRaw IsPermissiveStatement where
  getStatementLabel _                           = "isPermissive"
  getStatementContent (IsPermissiveStatement v) = toJSON v

data IsCopyleftStatement
  = IsCopyleftStatement Bool
instance FSRaw IsCopyleftStatement where
  getStatementLabel _                         = "isCopyleft"
  getStatementContent (IsCopyleftStatement v) = toJSON v

data HasLicenseText
  = HasLicenseText Text
instance FSRaw HasLicenseText where
  getStatementLabel _                    = "hasLicenseText"
  getStatementContent (HasLicenseText v) = toJSON v

data HasShortname
  = HasShortname Text
instance FSRaw HasShortname where
  getStatementLabel _                   = "hasShortname"
  getStatementContent (HasShortname sn) = String sn
