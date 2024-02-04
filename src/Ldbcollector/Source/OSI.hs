{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE OverloadedStrings #-}

module Ldbcollector.Source.OSI
  ( OSI (..),
    isOsiApproved,
  )
where

import Control.Monad.Except (runExceptT)
import Data.Text qualified as T
import Data.Vector qualified as V
import Ldbcollector.Model
import Network.Protocol.OpenSource.License qualified as OSI

newtype OSILicense
  = OSILicense OSI.OSILicense
  deriving (Eq, Show, Generic)

instance ToJSON OSILicense

isOsiApproved :: Maybe Bool -> LicenseStatement
isOsiApproved (Just True) = LicenseRating $ PositiveLicenseRating (ScopedLicenseTag "OSI" "Approved" NoLicenseTagText)
isOsiApproved (Just False) = LicenseRating $ NegativeLicenseRating (ScopedLicenseTag "OSI" "Rejected" NoLicenseTagText)
isOsiApproved Nothing = LicenseRating $ NegativeLicenseRating (ScopedLicenseTag "OSI" "Not-Approved" NoLicenseTagText)

instance LicenseFactC OSILicense where
  getType _ = "OSILicense"
  getApplicableLNs (OSILicense l) =
    (LN . newNLN "osi" . OSI.olId) l
      `AlternativeLNs` ((LN . newLN . OSI.olName) l : map (\i -> LN $ newNLN (OSI.oiScheme i) (OSI.oiIdentifier i)) (OSI.olIdentifiers l))
      `ImpreciseLNs` map (LN . newLN . OSI.oonName) (OSI.olOther_names l)
  getImpliedStmts osil@(OSILicense l) =
    let urls = (map (\link -> (LicenseUrl ((Just . unpack . OSI.olNote) link) . unpack . OSI.olUrl) link) . OSI.olLinks) l
        keywords =
          map
            ( \kw -> case kw of
                "osi-approved" -> isOsiApproved (Just True)
                "discouraged" -> LicenseRating $ NegativeLicenseRating (ScopedLicenseTag "OSI-keyword" kw NoLicenseTagText)
                "non-reusable" -> LicenseRating $ NegativeLicenseRating (ScopedLicenseTag "OSI-keyword" kw NoLicenseTagText)
                "retired" -> LicenseRating $ NegativeLicenseRating (ScopedLicenseTag "OSI-keyword" kw NoLicenseTagText)
                "redundant" -> LicenseRating $ NegativeLicenseRating (ScopedLicenseTag "OSI-keyword" kw NoLicenseTagText)
                "popular" -> LicenseRating $ PositiveLicenseRating (ScopedLicenseTag "OSI-keyword" kw NoLicenseTagText)
                "permissive" -> LicenseType Permissive
                "copyleft" -> LicenseType Copyleft
                "special-purpose" -> LicenseRating $ NeutralLicenseRating (ScopedLicenseTag "OSI-keyword" kw NoLicenseTagText)
                _ -> (stmt . T.unpack) kw
            )
            (OSI.olKeywords l)
     in urls ++ keywords

data OSI = OSI

instance HasOriginalData OSI where
  getOriginalData OSI =
    FromUrl "https://opensource.org/licenses/" $
      FromUrl "https://api.opensource.org/licenses/" $
        FromUrl
          "https://github.com/OpenSourceOrg/licenses"
          NoPreservedOriginalData

instance Source OSI where
  getSource _ = Source "OSI"
  getFacts OSI = do
    response <- runExceptT OSI.allLicenses
    case response of
      Left err -> do
        stderrLogIO $ "Error: " ++ err
        pure mempty
      Right licenses -> (return . V.fromList . map (wrapFact . OSILicense)) licenses