module Ldbcollector.Source
  ( module X,
    SourceEntry (..),
    sourceEntries,
    applySources,
  )
where

import Data.Set qualified as Set
import Ldbcollector.Model
import Ldbcollector.Source.BlueOak
import Ldbcollector.Source.Cavil
import Ldbcollector.Source.ChooseALicense
import Ldbcollector.Source.Curation as X
import Ldbcollector.Source.EclipseOrgLegal
import Ldbcollector.Source.FOSSLight
import Ldbcollector.Source.FSF
import Ldbcollector.Source.Fedora
import Ldbcollector.Source.FossLicense
import Ldbcollector.Source.Fossology
import Ldbcollector.Source.GoogleLicensePolicy
import Ldbcollector.Source.Hermine
import Ldbcollector.Source.HitachiOpenLicense
import Ldbcollector.Source.Ifross
import Ldbcollector.Source.LicenseLynx
import Ldbcollector.Source.Metaeffekt
import Ldbcollector.Source.OKFN
import Ldbcollector.Source.ORT
import Ldbcollector.Source.OSADL
import Ldbcollector.Source.OSI
import Ldbcollector.Source.OSLC
import Ldbcollector.Source.OpenSourceOrg
import Ldbcollector.Source.SPDX
import Ldbcollector.Source.Scancode
import Ldbcollector.Source.TLDR
import Ldbcollector.Source.Warpr

-- | A named source entry: the name is used for --disable-<name> flags.
data SourceEntry = SourceEntry
  { seName :: String,
    seAction :: LicenseGraphM ()
  }

-- | All available source entries (except Curation, which is always applied).
sourceEntries :: [SourceEntry]
sourceEntries =
  [ SourceEntry "SPDX" $ applySource (SPDXData "./data/spdx-license-list-data/json/details/"),
    SourceEntry "OSI" $ applySource OSI,
    SourceEntry "OpenSourceOrg" $ applySource (OpenSourceOrgLicenses "./data/OpenSourceOrg-licenses.json"),
    SourceEntry "GoogleLicensePolicy" $ applySource (GoogleLicensePolicy "./data/google-licensecheck.license_type.go.json"),
    SourceEntry "Fedora" $ applySource (FedoraLicenseData "./data/fedora-legal-fedora-license-data.jsons"),
    SourceEntry "BlueOakCouncil" $ applySource (BlueOakCouncilLicenseList "./data/blueoakcouncil/blue-oak-council-license-list.json"),
    SourceEntry "BlueOakCouncilCopyleft" $ applySource (BlueOakCouncilCopyleftList "./data/blueoakcouncil/blue-oak-council-copyleft-list.json"),
    SourceEntry "OSADL" $ applySource (OSADL "./data/OSADL-checklists"),
    SourceEntry "FSF" $ applySource (FSF "./data/wking-fsf-api"),
    SourceEntry "ChooseALicense" $ applySource (ChooseALicense "./data/github-choosealicense.com/_licenses/"),
    SourceEntry "Scancode" $ applySource (ScancodeLicenseDB "./data/nexB-scancode-licensedb/docs/"),
    SourceEntry "OSLC" $ applySource (OSLC "./data/finos-OSLC-handbook/src/"),
    SourceEntry "Fossology" $ applySource (FossologyLicenseRef "./data/fossology/licenseRef.json"),
    SourceEntry "OKFN" $ applySource (OKFN "./data/okfn-licenses/licenses/groups/all.json"),
    SourceEntry "ORT-ort-config" $ applySource (OrtLicenseClassifications "ort-config" "./data/oss-review-toolkit-ort-config/license-classifications.yml"),
    SourceEntry "ORT-doubleopen" $ applySource (OrtLicenseClassifications "doubleopen" "./data/doubleopen-project-policy-configuration/license-classifications.yml"),
    SourceEntry "Cavil" $ applySource (CavilLicenseChanges "./data/openSUSE-cavil/lib/Cavil/resources/license_changes.txt"),
    SourceEntry "Metaeffekt" $ applySource (Metaeffekt True "./data/org-metaeffekt-metaeffekt-universe/src/main/resources/ae-universe"),
    SourceEntry "Hermine" $ applySource (HermineData "./data/hermine-project-hermine-data"),
    SourceEntry "Warpr" $ applySource (Warpr "./data/warpr-licensedb/data"),
    SourceEntry "FossLicense" $ applySource (FossLicenseVar "./data/hesa-foss-licenses/var"),
    SourceEntry "FOSSLight" $ applySource (FOSSLight "./data/fosslight/fosslight.sqlite.db"),
    SourceEntry "HitachiOpenLicense" $ applySource (HitachiOpenLicense "./data/Hitachi-open-license/data" "./data/Hitachi-open-license.translations.csv"),
    SourceEntry "Eclipse" $ applySource (EclipseOrgLegal "./data/eclipse.org-legal-licenses.json"),
    SourceEntry "Ifross" $ applySource (Ifross "./data/ifrOSS-ifrOSS.yaml"),
    SourceEntry "LicenseLynx" $ applySource (LicenseLynxData "./data/licenselynx-licenselynx/data"),
    SourceEntry "TLDR" $ applySource (TLDRLicenseNamings "data/tldrlegal/tldrLicenses.csv")
  ]

applySources :: Set.Set String -> Vector CurationItem -> LicenseGraphM ()
applySources disabledSources curation = do
  lift $ infoM rootLoggerName "# get sources ..."
  let enabledEntries = filter (\e -> not $ Set.member (seName e) disabledSources) sourceEntries
  unless (Set.null disabledSources) $
    lift $
      infoM rootLoggerName $
        "# disabled sources: " ++ show (Set.toList disabledSources)
  mapM_ seAction enabledEntries
  applySource (Curation curation)
  lift $ infoM rootLoggerName "# ... got sources"
