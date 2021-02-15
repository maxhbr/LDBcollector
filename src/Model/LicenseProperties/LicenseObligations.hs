{-# LANGUAGE ExistentialQuantification #-}
{-# LANGUAGE TypeFamilies #-}
{-# LANGUAGE GADTs #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE DeriveGeneric #-}
module Model.LicenseProperties.LicenseObligations
    where

import qualified Prelude as P
import           MyPrelude

import qualified Data.Text as T
import qualified Data.Vector as V
import qualified Data.Map as M
import qualified Text.Pandoc.Builder as P

{-
     License_Unknown
      | \
      |  - OpenSourceLicense_Unknown
      |     | \
      |     \  - OpenSourceLicense_NoCopyleft
      |      - OpenSourceLicense_Copyleft <CopyleftKind>
      \
       - NonOpenSourceLicense
          | | \
          | \  - PublicDomain
          \  - ProprietaryFreeLicense
           - CommercialLicense
-}
-- data LicenseTaxonomy
--   = License_Unknown
--   | OpenSourceLicense_Unknown
--   | OpenSourceLicense_Copyleft CopyleftKind
--   | OpenSourceLicense_NoCopyleft
--   | NonOpenSourceLicense
--   | PublicDomain
--   | ProprietaryFreeLicense
--   | CommercialLicense
--   deriving (Eq, Show, Generic)
-- instance ToJSON LicenseTaxonomy

data ImpliedRight
  = ImpliedRight String
  | ImpliedRightWithDesc String String
  deriving (Eq, Generic)
instance Show ImpliedRight where
  show (ImpliedRight r) = r
  show (ImpliedRightWithDesc r desc) = r ++ " (" ++ desc ++ ")"
instance ToJSON ImpliedRight
data ImpliedCondition
  = ImpliedCondition String
  | ImpliedConditionWithDesc String String
  deriving (Eq, Generic)
instance Show ImpliedCondition where
  show (ImpliedCondition c) = c
  show (ImpliedConditionWithDesc c desc) = c ++ " (" ++ desc ++ ")"
instance ToJSON ImpliedCondition
data ImpliedLimitation
  = ImpliedLimitation String
  | ImpliedLimitationWithDesc String String
  deriving (Eq, Generic)
instance Show ImpliedLimitation where
  show (ImpliedLimitation l) = l
  show (ImpliedLimitationWithDesc l desc) = l ++ " (" ++ desc ++ ")"
instance ToJSON ImpliedLimitation
data LicenseObligations
  = LicenseObligations [ImpliedRight] [ImpliedCondition] [ImpliedLimitation]
  deriving (Eq, Show, Generic)
instance ToJSON LicenseObligations where
  toJSON (LicenseObligations irs ics ils) = object [ "rights" .= irs
                                                   , "conditions" .= ics
                                                   , "limitations" .= ils ]

instance Blockable LicenseObligations where
  toBlock (LicenseObligations rights conditions limitations) = P.simpleTable (map (P.para . P.text)
                                                                              ["Rights:", "Conditions:", "Limitations:"])
                                                                             [[ P.bulletList (map (P.para . pShow) rights)
                                                                              ,  P.bulletList (map (P.para . pShow) conditions)
                                                                              , P.bulletList (map (P.para . pShow) limitations) ]]
