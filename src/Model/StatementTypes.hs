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

data ObligationStatement
  = ImpliesRight String
  | ImpliesCondition String
  | ImpliesLimitation String
instance FSRaw ObligationStatement where
  getStatementLabel (ImpliesRight _) = "impliesRight"
  getStatementLabel (ImpliesCondition _) = "impliesCondition"
  getStatementLabel (ImpliesLimitation _) = "impliesLimitation"
  getStatementContent (ImpliesRight c) = toJSON c
  getStatementContent (ImpliesCondition c) = toJSON c
  getStatementContent (ImpliesLimitation c) = toJSON c

data LicenseRating
  = PossitiveLicenseRating Text
  | NegativeLicenseRating Text
instance FSRaw LicenseRating where
  getStatementContent (PossitiveLicenseRating _) = "possitiveRating"
  getStatementContent (NegativeLicenseRating _) = "negativeRating"
  getStatementContent (PossitiveLicenseRating desc) = toJSON desc
  getStatementContent (NegativeLicenseRating desc) = toJSON desc
