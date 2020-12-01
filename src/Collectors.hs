module Collectors
  ( module X
  , allCollectors
  ) where

import           Model.License as X

import           Collectors.Common as X (Collector (..))
import           Collectors.Override as X

import           Collectors.BlueOak as X
import           Collectors.Cavil as X
import           Collectors.ChooseALicense as X
import           Collectors.DFSG as X
import           Collectors.FedoraProjectWiki as X
import           Collectors.Fossology as X
import           Collectors.Gnu as X
import           Collectors.Google as X
import           Collectors.IfrOSS as X
import           Collectors.LicenseCompatibility as X
import           Collectors.LicenseCompatibilityChecker as X
import           Collectors.OKFN as X
import           Collectors.OSADL as X
import           Collectors.OSI as X
import           Collectors.OSLC as X
import           Collectors.OpenChainPolicyTemplate as X
import           Collectors.OpenLicense as X
import           Collectors.SPDX as X
import           Collectors.Scancode as X
import           Collectors.Wikipedia as X


allCollectors :: [(LicenseFactClassifier, IO Facts)]
allCollectors = let
  toTpl c = (getLicenseFactClassifier c, loadFacts c)
  in
  [ toTpl blueOakCollector
  , (cavilLFC, loadCavilFacts)
  , (calLFC, loadChooseALicenseFacts)
  , (dfsgLFC, loadDFSGFacts)
  , (fedoraLFC, loadFedoraFacts)
  , (fossologyLFC, loadFossologyFacts)
  , (gnuLFC, loadGnuFacts)
  , (googleLFC, loadGoogleFacts)
  , (ifrOSSLFC, loadIfrOSSFacts)
  , (licenseCompatibilityCheckerLFC, loadLicenseCompatibilityCheckerFacts)
  , (licenseCompatibilityLFC, loadLicenseCompatibilityFacts)
  , (okfnLFC, loadOkfnFacts)
  , (osadlLFC, loadOsadlFacts)
  , (osiLFC, loadOSIFacts)
  , (oslcLFC, loadOslcFacts)
  , (ocptLFC, loadOCPTFacts)
  , (olLFC, loadOpenLicenseFacts)
  , (spdxLFC, loadSPDXFacts)
  , (scancodeLFC, loadScancodeFacts)
  , (wikipediaLFC, loadWikipediaFacts)
  ]
