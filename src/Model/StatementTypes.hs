{-# LANGUAGE OverloadedStrings #-}
module Model.StatementTypes
  where

import           Data.Aeson
import           Data.Text (Text)

import Model.Fact

data IsPermissiveStatement
  = IsPermissiveStatement Bool (Maybe Text)

instance FSRaw IsPermissiveStatement where
  getStatementLabel _                                    = "isPermissive"
  getStatementContent (IsPermissiveStatement v _)        = toJSON v
  getStatementDescription (IsPermissiveStatement _ desc) = desc

data IsCopyleftStatement
  = IsCopyleftStatement Bool (Maybe Text)

instance FSRaw IsCopyleftStatement where
  getStatementLabel _                                  = "isCopyleft"
  getStatementContent (IsCopyleftStatement v _)        = toJSON v
  getStatementDescription (IsCopyleftStatement _ desc) = desc

data HasLicenseText
  = HasLicenseText Text (Maybe Text)

instance FSRaw HasLicenseText where
  getStatementLabel _                             = "hasLicenseText"
  getStatementContent (HasLicenseText v _)        = toJSON v
  getStatementDescription (HasLicenseText _ desc) = desc
