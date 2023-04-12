module Ldbcollector.Source where

import           Ldbcollector.Model
import           Ldbcollector.Source.BlueOak
import           Ldbcollector.Source.Cavil
import           Ldbcollector.Source.ChooseALicense
import           Ldbcollector.Source.EclipseOrgLegal
import           Ldbcollector.Source.Fedora
import           Ldbcollector.Source.FOSSLight
import           Ldbcollector.Source.Fossology
import           Ldbcollector.Source.FSF
import           Ldbcollector.Source.HitachiOpenLicense
import           Ldbcollector.Source.Metaeffekt
import           Ldbcollector.Source.OKFN
import           Ldbcollector.Source.OSADL
import           Ldbcollector.Source.OSI
import           Ldbcollector.Source.OSLC
import           Ldbcollector.Source.Scancode
import           Ldbcollector.Source.SPDX
import           Ldbcollector.Source.Warpr

applySources :: LicenseGraphM ()
applySources = do
    lift $ infoM rootLoggerName "# get sources ..."
    applySource SPDXLicenseIds
    -- applySource OSI
    applySource (FedoraLicenseData "./data/fedora-legal-fedora-license-data.jsons")
    applySource (BlueOakCouncilLicenseList "./data/blueoakcouncil/blue-oak-council-license-list.json")
    applySource (BlueOakCouncilCopyleftList "./data/blueoakcouncil/blue-oak-council-copyleft-list.json")
    applySource (OSADL "./data/OSADL-checklists")
    applySource (FSF "./data/wking-fsf-api")
    applySource (ChooseALicense "./data/github-choosealicense.com/_licenses/")
    applySource (ScancodeLicenseDB "./data/nexB-scancode-licensedb/docs/")
    applySource (OSLC "./data/finos-OSLC-handbook/src/")
    applySource (FossologyLicenseRef "./data/fossology/licenseRef.json")
    applySource (OKFN "./data/okfn-licenses/licenses/groups/all.json")
    applySource (CavilLicenseChanges "./data/openSUSE-cavil/lib/Cavil/resources/license_changes.txt")
    applySource (Metaeffekt "./data/org-metaeffekt-metaeffekt-universe/src/main/resources/ae-universe")
    applySource (Warpr "./data/warpr-licensedb/data")
    applySource (FOSSLight "./data/fosslight/fosslight.sqlite.db")
    applySource (HitachiOpenLicense "./data/Hitachi-open-license/data" "./data/Hitachi-open-license.translations.csv")
    applySource (EclipseOrgLegal "data/eclipse.org-legal-licenses.json")
    lift $ infoM rootLoggerName "# ... got sources"
