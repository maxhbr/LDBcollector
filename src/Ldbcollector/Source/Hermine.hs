{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE QuasiQuotes #-}
{-# LANGUAGE TemplateHaskell #-}

module Ldbcollector.Source.Hermine
  ( HermineData (..),
  )
where


import Data.Vector qualified as V
import Ldbcollector.Model hiding (ByteString)
import Ldbcollector.Source.OSI (isOsiApproved)
import Text.Blaze.Html5 qualified as H

data PASSIVITY_CHOICES
    = ACTIVE
    | PASSIVE
    deriving (Eq, Ord, Generic)
instance Show PASSIVITY_CHOICES where
    show ACTIVE = "Active"
    show PASSIVE = "Passive"
instance FromJSON PASSIVITY_CHOICES where
    parseJSON = withText "PASSIVITY_CHOICES" $ \case
        "Active" -> return ACTIVE
        "Passive" -> return PASSIVE
        _ -> fail "Invalid PASSIVITY_CHOICES"
instance ToJSON PASSIVITY_CHOICES where
    toJSON ACTIVE = "Active"
    toJSON PASSIVE = "Passive"
data METACATEGORY_CHOICES
    = METACATEGORY_COMMUNICATION
    | METACATEGORY_IP_MANAGEMENT
    | METACATEGORY_LICENSE_AGREEMENT
    | METACATEGORY_MENTIONS
    | METACATEGORY_PROVIDING_SOURCE_CODE
    | METACATEGORY_TECHNICAL_CONSTRAINTS
    deriving (Eq, Ord, Generic)
instance Show METACATEGORY_CHOICES where
    show METACATEGORY_COMMUNICATION = "Communication constraints"
    show METACATEGORY_IP_MANAGEMENT = "IP management"
    show METACATEGORY_LICENSE_AGREEMENT = "License agreement"
    show METACATEGORY_MENTIONS = "Mentions"
    show METACATEGORY_PROVIDING_SOURCE_CODE = "Providing source code"
    show METACATEGORY_TECHNICAL_CONSTRAINTS = "Technical constraints"
instance FromJSON METACATEGORY_CHOICES where
    parseJSON = withText "METACATEGORY_CHOICES" $ \case
        "Communication" -> return METACATEGORY_COMMUNICATION
        "IPManagement" -> return METACATEGORY_IP_MANAGEMENT
        "LicenseAgreement" -> return METACATEGORY_LICENSE_AGREEMENT
        "Mentions" -> return METACATEGORY_MENTIONS
        "ProvidingSourceCode" -> return METACATEGORY_PROVIDING_SOURCE_CODE
        "TechnicalConstraints" -> return METACATEGORY_TECHNICAL_CONSTRAINTS
instance ToJSON METACATEGORY_CHOICES where
    toJSON METACATEGORY_COMMUNICATION = "Communication"
    toJSON METACATEGORY_IP_MANAGEMENT = "IPManagement"
    toJSON METACATEGORY_LICENSE_AGREEMENT = "LicenseAgreement"
    toJSON METACATEGORY_MENTIONS = "Mentions"
    toJSON METACATEGORY_PROVIDING_SOURCE_CODE = "ProvidingSourceCode"
    toJSON METACATEGORY_TECHNICAL_CONSTRAINTS = "TechnicalConstraints"

data HermineGeneric
    = HermineGeneric
    { hg_name :: !String,
      hg_description :: !String,
      hg_metacategory :: !(Maybe METACATEGORY_CHOICES),
      hg_passivity :: !(Maybe PASSIVITY_CHOICES)
    }
  deriving (Eq, Ord, Show, Generic)
$(deriveJSON defaultOptions {fieldLabelModifier = drop 3, constructorTagModifier = map toLower} ''HermineGeneric)

data HermineGenericRef
    = Unresolved !String
    | Resolved !HermineGeneric
    deriving (Eq, Ord, Show, Generic)

data HermineObligation
    = HermineObligation
    { ho_license :: ![String],
      ho_generic :: !(Maybe [String]), -- ![HermineGeneric],
      ho_name :: !String,
      ho_verbatim :: !String,
      ho_passivity :: !String,
      ho_trigger_expl :: !String,
      ho_trigger_mdf :: !String
    } deriving (Eq, Ord, Show, Generic)
$(deriveJSON defaultOptions {fieldLabelModifier = drop 3, constructorTagModifier = map toLower} ''HermineObligation)
instance H.ToMarkup HermineObligation where
  toMarkup ho = do
    H.h5 $ H.toMarkup (ho_name ho)
    H.pre $ H.toMarkup (ho_verbatim ho)
    H.p $ do
      H.strong "License:"
      H.ul $ forM_ (ho_license ho) $ \license -> do
        H.li $ H.toMarkup license
    case ho_generic ho of
      Just generics -> do
        H.p $ do
          H.strong "Generics:"
          H.ul $ forM_ generics $ \generic -> do
            H.li $ H.toMarkup generic
      _ -> return ()
    H.p $ do
      H.strong "Passivity:"
      H.toMarkup (ho_passivity ho)
    H.p $ do
      H.strong "Trigger explanation:"
      H.toMarkup (ho_trigger_expl ho)
    H.p $ do
      H.strong "Trigger modification:"
      H.toMarkup (ho_trigger_mdf ho)

data COPYLEFT_CHOICES
    = COPYLEFT_NONE -- "None"
    | COPYLEFT_STRONG -- "Strong"
    | COPYLEFT_WEAK -- "Weak"
    | COPYLEFT_NETWORK -- "Network"
    | COPYLEFT_NETWORK_WEAK -- "NetworkWeak"
    | COPYLEFT_NOT_REVIEWED -- ""
    deriving (Eq, Ord, Generic)
instance Show COPYLEFT_CHOICES where
    show COPYLEFT_NONE = "Permissive"
    show COPYLEFT_STRONG = "Strong copyleft"
    show COPYLEFT_WEAK = "Weak copyleft"
    show COPYLEFT_NETWORK = "Strong network copyleft"
    show COPYLEFT_NETWORK_WEAK = "Weak network copyleft"
    show COPYLEFT_NOT_REVIEWED = "Not reviewed yet"
instance FromJSON COPYLEFT_CHOICES where
    parseJSON = withText "COPYLEFT_CHOICES" $ \case
        "None" -> return COPYLEFT_NONE
        "Strong" -> return COPYLEFT_STRONG
        "Weak" -> return COPYLEFT_WEAK
        "Network" -> return COPYLEFT_NETWORK
        "NetworkWeak" -> return COPYLEFT_NETWORK_WEAK
        "" -> return COPYLEFT_NOT_REVIEWED
        _ -> fail "Invalid COPYLEFT_CHOICES"
instance ToJSON COPYLEFT_CHOICES where
    toJSON COPYLEFT_NONE = "None"
    toJSON COPYLEFT_STRONG = "Strong"
    toJSON COPYLEFT_WEAK = "Weak"
    toJSON COPYLEFT_NETWORK = "Network"
    toJSON COPYLEFT_NETWORK_WEAK = "NetworkWeak"
    toJSON COPYLEFT_NOT_REVIEWED = ""

data ALLOWED_CHOICES
    = ALLOWED_ALWAYS -- "always"
    | ALLOWED_NEVER -- "never"
    | ALLOWED_CONTEXT -- "context"
    | ALLOWED_NOTFOSS -- "notfoss"
    | ALLOWED_NOT_REVIEWED -- ""
    deriving (Eq, Ord, Generic)
instance Show ALLOWED_CHOICES where
    show ALLOWED_ALWAYS = "Always allowed"
    show ALLOWED_NEVER = "Never allowed"
    show ALLOWED_CONTEXT = "Allowed depending on context"
    show ALLOWED_NOTFOSS = "Out of FOSS Policy"
    show ALLOWED_NOT_REVIEWED = "Not reviewed yet"
    -- "", "Not reviewed yet"),
instance FromJSON ALLOWED_CHOICES where
    parseJSON = withText "ALLOWED_CHOICES" $ \case
        "always" -> return ALLOWED_ALWAYS
        "never" -> return ALLOWED_NEVER
        "context" -> return ALLOWED_CONTEXT
        "notfoss" -> return ALLOWED_NOTFOSS
        "" -> return ALLOWED_NOT_REVIEWED
        _ -> fail "Invalid ALLOWED_CHOICES"
instance ToJSON ALLOWED_CHOICES where
    toJSON ALLOWED_ALWAYS = "always"
    toJSON ALLOWED_NEVER = "never"
    toJSON ALLOWED_CONTEXT = "context"
    toJSON ALLOWED_NOTFOSS = "notfoss"
    toJSON ALLOWED_NOT_REVIEWED = ""

data FOSS_CHOICES
    = FOSS_YES -- "Yes"
    | FOSS_YES_AUTO -- "Yes-Auto"
    | FOSS_NO -- "No"
    | FOSS_NO_AUTO -- "No-Auto"
    | FOSS_NOT_REVIEWED -- ""
    deriving (Eq, Ord, Generic)
instance Show FOSS_CHOICES where
    show FOSS_YES = "We consider it is FOSS"
    show FOSS_YES_AUTO = "FOSS - deduced"
    show FOSS_NO = "We consider it is NOT FOSS"
    show FOSS_NO_AUTO = "NOT FOSS - deduced"
    show FOSS_NOT_REVIEWED = "Not reviewed yet"
instance FromJSON FOSS_CHOICES where
    parseJSON = withText "FOSS_CHOICES" $ \case
        "Yes" -> return FOSS_YES
        "Yes-Auto" -> return FOSS_YES_AUTO
        "No" -> return FOSS_NO
        "No-Auto" -> return FOSS_NO_AUTO
        "" -> return FOSS_NOT_REVIEWED
        _ -> fail "Invalid FOSS_CHOICES"
instance ToJSON FOSS_CHOICES where
    toJSON FOSS_YES = "Yes"
    toJSON FOSS_YES_AUTO = "Yes-Auto"
    toJSON FOSS_NO = "No"
    toJSON FOSS_NO_AUTO = "No-Auto"
    toJSON FOSS_NOT_REVIEWED = ""

data STATUS_CHOICES
    = STATUS_CHECKED -- "Checked"
    | STATUS_PENDING -- "Pending"
    | STATUS_TO_DISCUSS -- "To_Discuss"
    | STATUS_TO_CHECK -- "To_Check"
    deriving (Eq, Ord, Generic)
instance Show STATUS_CHOICES where
    show STATUS_CHECKED = "Checked"
    show STATUS_PENDING = "Pending"
    show STATUS_TO_DISCUSS = "To discuss"
    show STATUS_TO_CHECK = "To check"
instance FromJSON STATUS_CHOICES where
    parseJSON = withText "STATUS_CHOICES" $ \case
        "Checked" -> return STATUS_CHECKED
        "Pending" -> return STATUS_PENDING
        "To_Discuss" -> return STATUS_TO_DISCUSS
        "To_Check" -> return STATUS_TO_CHECK
        _ -> fail "Invalid STATUS_CHOICES"
instance ToJSON STATUS_CHOICES where
    toJSON STATUS_CHECKED = "Checked"
    toJSON STATUS_PENDING = "Pending"
    toJSON STATUS_TO_DISCUSS = "To_Discuss"
    toJSON STATUS_TO_CHECK = "To_Check"

data LIABILITY_CHOICES
    = LIABILITY_FULL -- "Full"
    | LIABILITY_PARTIAL -- "Partial"
    | LIABILITY_ABSENT -- "Absent"
    deriving (Eq, Ord, Generic)
instance Show LIABILITY_CHOICES where
    show LIABILITY_FULL = "Full clause"
    show LIABILITY_PARTIAL = "Partial clause"
    show LIABILITY_ABSENT = "No clause"
instance FromJSON LIABILITY_CHOICES where
    parseJSON = withText "LIABILITY_CHOICES" $ \case
        "Full" -> return LIABILITY_FULL
        "Partial" -> return LIABILITY_PARTIAL
        "Absent" -> return LIABILITY_ABSENT
        _ -> fail "Invalid LIABILITY_CHOICES"
instance ToJSON LIABILITY_CHOICES where
    toJSON LIABILITY_FULL = "Full"
    toJSON LIABILITY_PARTIAL = "Partial"
    toJSON LIABILITY_ABSENT = "Absent"

data WARRANTY_CHOICES
    = WARRANTY_FULL -- "Full"
    | WARRANTY_PARTIAL -- "Partial"
    | WARRANTY_ABSENT -- "Absent"
    deriving (Eq, Ord, Generic)
instance Show WARRANTY_CHOICES where
    show WARRANTY_FULL = "Full clause"
    show WARRANTY_PARTIAL = "Partial clause"
    show WARRANTY_ABSENT = "No clause"
instance FromJSON WARRANTY_CHOICES where
    parseJSON = withText "WARRANTY_CHOICES" $ \case
        "Full" -> return WARRANTY_FULL
        "Partial" -> return WARRANTY_PARTIAL
        "Absent" -> return WARRANTY_ABSENT
        _ -> fail "Invalid WARRANTY_CHOICES"
instance ToJSON WARRANTY_CHOICES where
    toJSON WARRANTY_FULL = "Full"
    toJSON WARRANTY_PARTIAL = "Partial"
    toJSON WARRANTY_ABSENT = "Absent"

data HermineLicense
    = HermineLicense
    { hl_spdx_id :: !String,
      hl_long_name :: !String,
      hl_license_version :: !String,
      hl_radical :: !(Maybe String), -- TODO: Just "" -> Nothing
      hl_autoupgrade :: Maybe Bool,
      hl_steward :: !String,
      hl_inspiration_spdx :: !(Maybe String), -- TODO: Just "" -> Nothing, SPDX Identifier of another license which inspired this one
      hl_copyleft :: !COPYLEFT_CHOICES,
      hl_url :: !String,
      hl_osi_approved :: Maybe Bool,
      hl_fsf_approved :: Maybe Bool,
      hl_foss :: !FOSS_CHOICES,
      hl_patent_grant :: Maybe Bool,
      hl_ethical_clause :: Maybe Bool,
      hl_non_commercial :: Maybe Bool,
      hl_non_tivoisation :: Maybe Bool,
      hl_law_choice :: !(Maybe String), -- TODO: Just "" -> Nothing
      hl_comment :: !(Maybe Text), -- TODO: Just "" -> Nothing
      hl_verbatim :: !(Maybe Text), -- TODO: Just "" -> Nothing
      hl_obligations :: [HermineObligation]
    } deriving (Eq, Ord, Show, Generic)
$(deriveJSON defaultOptions {fieldLabelModifier = drop 3, constructorTagModifier = map toLower} ''HermineLicense)

instance LicenseFactC HermineLicense where
  getType _ = "HermineLicense"
  getApplicableLNs hl =
    (LN . newNLN "spdx" . pack . hl_spdx_id) hl
      `AlternativeLNs` [ (LN . newLN . pack . hl_long_name) hl
                       ]
  getImpliedStmts hl = let
        copyleft_stmt = case hl_copyleft hl of
                           COPYLEFT_NONE -> LicenseType Permissive
                           COPYLEFT_STRONG -> LicenseType StronglyProtective
                           COPYLEFT_WEAK -> LicenseType WeaklyProtective
                           COPYLEFT_NETWORK -> LicenseType NetworkProtective
                           COPYLEFT_NETWORK_WEAK -> LicenseType (UnknownLicenseType (Just "Weak network copyleft"))
                           COPYLEFT_NOT_REVIEWED -> noStmt
        foss_stmt = let
                foss = hl_foss hl
                foss_tag = ScopedLicenseTag (getType hl) (tShow foss) NoLicenseTagText
            in case foss of
                      FOSS_YES -> LicenseRating (PositiveLicenseRating foss_tag)
                      FOSS_YES_AUTO -> LicenseRating (PositiveLicenseRating foss_tag)
                      FOSS_NO -> LicenseRating (NegativeLicenseRating foss_tag)
                      FOSS_NO_AUTO -> LicenseRating (NegativeLicenseRating foss_tag)
                      FOSS_NOT_REVIEWED -> noStmt
        comment_stmt = case hl_comment hl of
                         Just comment -> commentStmt (getType hl) comment
                         Nothing -> noStmt
        non_commercial_stmt = case hl_non_commercial hl of
                                Just True -> LicenseRating (NegativeLicenseRating (ScopedLicenseTag (getType hl) "Non-commercial clause" NoLicenseTagText))
                                _ -> noStmt
        osi_stmt = isOsiApproved (hl_osi_approved hl)
        fst_stmt = case hl_fsf_approved hl of
                     Just True -> LicenseRating (PositiveLicenseRating (ScopedLicenseTag "FSF" "Approved" NoLicenseTagText))
                     Just False -> LicenseRating (NegativeLicenseRating (ScopedLicenseTag "FSF" "Rejected" NoLicenseTagText))
                     _ -> noStmt
        text_stmt = case hl_verbatim hl of
                       Just verbatim -> LicenseText verbatim
                       Nothing -> noStmt
        url_stmts = map (LicenseUrl Nothing) [hl_url hl]
        other_stmts = [ ifToStmt (show (hl_spdx_id hl) ++ " is a license with a patent grant") (fromMaybe False (hl_patent_grant hl)),
                        ifToStmt (show (hl_spdx_id hl) ++ " is a license with an ethical clause") (fromMaybe False (hl_ethical_clause hl)),
                        ifToStmt (show (hl_spdx_id hl) ++ " is a license with a non-tivoisation clause") (fromMaybe False (hl_non_tivoisation hl)),
                        (case hl_radical hl of
                           Just radical -> commentStmt (getType hl) (pack $ show (hl_spdx_id hl) ++ " is of radical: " ++ radical)
                           Nothing -> noStmt)
                      ]
    in copyleft_stmt : foss_stmt : comment_stmt : osi_stmt : text_stmt : url_stmts ++ other_stmts
  toMarkup hl = do
    H.h4 "Obligations"
    H.ul $ forM_ (hl_obligations hl) $ \obligation -> do
      H.li $ do
        H.toMarkup obligation

newtype HermineData = HermineData FilePath

instance HasOriginalData HermineData where
  getOriginalData (HermineData dir) =
      FromUrl "https://gitlab.com/hermine-project/hermine-data" $
        FromFile dir NoPreservedOriginalData

instance Source HermineData where
  getSource _ = Source "HermineData"
  getFacts (HermineData dir) =
    let parseOrFailJson json = do
          logFileReadIO json
          decoded <- eitherDecodeFileStrict json :: IO (Either String HermineLicense)
          case decoded of
            Left err -> fail err
            Right hermineLicense -> return hermineLicense
     in do
          hermineGenericsJsons <- glob (dir </> "generics" </> "*.json")
          hermineLicenseJsons <- glob (dir </> "licenses" </> "*.json")
          hermineLicenses <- mapM parseOrFailJson hermineLicenseJsons
          (return . V.fromList) (wrapFacts hermineLicenses)
