;
; Copyright © 2021 Peter Monks
;
; Licensed under the Apache License, Version 2.0 (the "License");
; you may not use this file except in compliance with the License.
; You may obtain a copy of the License at
;
;     http://www.apache.org/licenses/LICENSE-2.0
;
; Unless required by applicable law or agreed to in writing, software
; distributed under the License is distributed on an "AS IS" BASIS,
; WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
; See the License for the specific language governing permissions and
; limitations under the License.
;
; SPDX-License-Identifier: Apache-2.0
;

(ns lice-comb.spdx-test
  (:require [clojure.test               :refer [deftest testing is use-fixtures]]
            [clojure.java.io            :as io]
            [lice-comb.test-boilerplate :refer [fixture]]
            [lice-comb.spdx             :refer [fuzzy-match-name->license-ids fuzzy-match-uri->license-ids text->ids]]))

(use-fixtures :once fixture)

; Note: these tests should be extended indefinitely, as it exercises the most-utilised part of the library (matching license names found in POMs)
(deftest fuzzy-match-name->license-ids-tests
  (testing "Nil, empty or blank names"
    (is (nil?                                      (fuzzy-match-name->license-ids nil)))
    (is (nil?                                      (fuzzy-match-name->license-ids "")))
    (is (nil?                                      (fuzzy-match-name->license-ids "       ")))
    (is (nil?                                      (fuzzy-match-name->license-ids "\n")))
    (is (nil?                                      (fuzzy-match-name->license-ids "\t"))))
  (testing "Names that are SPDX license ids"
    (is (= #{"AGPL-3.0"}                           (fuzzy-match-name->license-ids "AGPL-3.0")))
    (is (= #{"AGPL-3.0-only"}                      (fuzzy-match-name->license-ids "AGPL-3.0-only")))
    (is (= #{"Apache-2.0"}                         (fuzzy-match-name->license-ids "    Apache-2.0        ")))   ; Test whitespace
    (is (= #{"Apache-2.0"}                         (fuzzy-match-name->license-ids "Apache-2.0")))
    (is (= #{"CC-BY-SA-4.0"}                       (fuzzy-match-name->license-ids "CC-BY-SA-4.0")))
    (is (= #{"GPL-2.0"}                            (fuzzy-match-name->license-ids "GPL-2.0")))
    (is (= #{"GPL-2.0-with-classpath-exception"}   (fuzzy-match-name->license-ids "GPL-2.0-with-classpath-exception"))))
  (testing "Names"
    (is (= #{"AGPL-3.0"}                           (fuzzy-match-name->license-ids "GNU Affero General Public License (AGPL) version 3.0")))
    (is (= #{"AGPL-3.0"}                           (fuzzy-match-name->license-ids "GNU Affero General Public License v3.0")))
    (is (= #{"AGPL-3.0-only"}                      (fuzzy-match-name->license-ids "GNU Affero General Public License v3.0 only")))
    (is (= #{"Apache-1.0"}                         (fuzzy-match-name->license-ids "Apache Software License")))
    (is (= #{"Apache-1.0"}                         (fuzzy-match-name->license-ids "Apache License 1")))
    (is (= #{"Apache-1.0"}                         (fuzzy-match-name->license-ids "Apache License 1.0")))
    (is (= #{"Apache-1.0"}                         (fuzzy-match-name->license-ids "Apache License Version 1.0")))
    (is (= #{"Apache-1.0"}                         (fuzzy-match-name->license-ids "Apache License, Version 1.0")))
    (is (= #{"Apache-1.0"}                         (fuzzy-match-name->license-ids "Apache Software License - Version 1.0")))
    (is (= #{"Apache-1.1"}                         (fuzzy-match-name->license-ids "Apache License 1.1")))
    (is (= #{"Apache-1.1"}                         (fuzzy-match-name->license-ids "Apache License Version 1.1")))
    (is (= #{"Apache-1.1"}                         (fuzzy-match-name->license-ids "Apache License, Version 1.1")))
    (is (= #{"Apache-1.1"}                         (fuzzy-match-name->license-ids "Apache Software License - Version 1.1")))
    (is (= #{"Apache-1.1"}                         (fuzzy-match-name->license-ids "The MX4J License, version 1.0")))
    (is (= #{"Apache-2.0"}                         (fuzzy-match-name->license-ids "               Apache Software License, Version 2.0             ")))   ; Test whitespace
    (is (= #{"Apache-2.0"}                         (fuzzy-match-name->license-ids "Apache 2.0")))
    (is (= #{"Apache-2.0"}                         (fuzzy-match-name->license-ids "Apache License 2.0")))
    (is (= #{"Apache-2.0"}                         (fuzzy-match-name->license-ids "Apache License Version 2.0")))
    (is (= #{"Apache-2.0"}                         (fuzzy-match-name->license-ids "Apache License, Version 2.0")))
    (is (= #{"Apache-2.0"}                         (fuzzy-match-name->license-ids "Apache Software License - Version 2.0")))
    (is (= #{"Apache-2.0"}                         (fuzzy-match-name->license-ids "Apache Software License 2")))
    (is (= #{"Apache-2.0"}                         (fuzzy-match-name->license-ids "Apache Software License 2.0")))
    (is (= #{"Apache-2.0"}                         (fuzzy-match-name->license-ids "Apache Software License Version 2")))
    (is (= #{"Apache-2.0"}                         (fuzzy-match-name->license-ids "Apache Software License Version 2.0")))
    (is (= #{"Apache-2.0"}                         (fuzzy-match-name->license-ids "Apache Software License v2")))
    (is (= #{"Apache-2.0"}                         (fuzzy-match-name->license-ids "Apache Software License v2.0")))
    (is (= #{"Apache-2.0"}                         (fuzzy-match-name->license-ids "Apache Software License, Version 2.0")))
    (is (= #{"Apache-2.0"}                         (fuzzy-match-name->license-ids "Apache v2")))
    (is (= #{"Apache-2.0"}                         (fuzzy-match-name->license-ids "The Apache Software License, Version 2.0")))
    (is (= #{"MIT"}                                (fuzzy-match-name->license-ids "Bouncy Castle Licence")))  ; Note spelling of "licence"
    (is (= #{"BSD-3-Clause"}                       (fuzzy-match-name->license-ids "3-Clause BSD License")))
    (is (= #{"BSD-3-Clause"}                       (fuzzy-match-name->license-ids "BSD 3-Clause License")))
    (is (= #{"BSD-3-Clause"}                       (fuzzy-match-name->license-ids "The BSD 3-Clause License (BSD3)")))
    (is (= #{"BSD-3-Clause-Attribution"}           (fuzzy-match-name->license-ids "BSD 3-Clause Attribution")))
    (is (= #{"CC-BY-3.0"}                          (fuzzy-match-name->license-ids "Attribution 3.0 Unported")))
    (is (= #{"CC-BY-3.0"}                          (fuzzy-match-name->license-ids "Creative Commons Legal Code Attribution 3.0 Unported")))
    (is (= #{"CC-BY-4.0"}                          (fuzzy-match-name->license-ids "Attribution 4.0 International")))
    (is (= #{"CC-BY-SA-4.0"}                       (fuzzy-match-name->license-ids "Creative Commons Attribution Share Alike 4.0 International")))
    (is (= #{"CDDL-1.0"}                           (fuzzy-match-name->license-ids "COMMON DEVELOPMENT AND DISTRIBUTION LICENSE Version 1")))
    (is (= #{"CDDL-1.0"}                           (fuzzy-match-name->license-ids "COMMON DEVELOPMENT AND DISTRIBUTION LICENSE Version 1.0")))
    (is (= #{"CDDL-1.0"}                           (fuzzy-match-name->license-ids "COMMON DEVELOPMENT AND DISTRIBUTION LICENSE (CDDL) Version 1.0")))
    (is (= #{"CDDL-1.1"}                           (fuzzy-match-name->license-ids "COMMON DEVELOPMENT AND DISTRIBUTION LICENSE Version 1.1")))
    (is (= #{"CDDL-1.1"}                           (fuzzy-match-name->license-ids "COMMON DEVELOPMENT AND DISTRIBUTION LICENSE (CDDL) Version 1.1")))
    (is (= #{"EPL-1.0"}                            (fuzzy-match-name->license-ids "Eclipse Public License")))
    (is (= #{"EPL-1.0"}                            (fuzzy-match-name->license-ids "Eclipse Public License (EPL)")))
    (is (= #{"EPL-1.0"}                            (fuzzy-match-name->license-ids "Eclipse Public License - v 1.0")))
    (is (= #{"EPL-1.0"}                            (fuzzy-match-name->license-ids "Eclipse Public License 1.0")))
    (is (= #{"EPL-1.0"}                            (fuzzy-match-name->license-ids "Eclipse Public License")))
    (is (= #{"EPL-1.0"}                            (fuzzy-match-name->license-ids "Eclipse Public License, Version 1.0")))
    (is (= #{"EPL-2.0"}                            (fuzzy-match-name->license-ids "Eclipse Public License 2.0")))
    (is (= #{"EPL-2.0"}                            (fuzzy-match-name->license-ids "Eclipse Public License version 2")))
    (is (= #{"GPL-2.0"}                            (fuzzy-match-name->license-ids "GNU General Public License, version 2")))
    (is (= #{"GPL-2.0-with-classpath-exception"}   (fuzzy-match-name->license-ids "GNU General Public License, version 2 (GPL2), with the classpath exception")))
    (is (= #{"GPL-2.0-with-classpath-exception"}   (fuzzy-match-name->license-ids "GNU General Public License, version 2 with the GNU Classpath Exception")))
    (is (= #{"GPL-2.0-with-classpath-exception"}   (fuzzy-match-name->license-ids "GNU General Public License v2.0 w/Classpath exception")))
    (is (= #{"JSON"}                               (fuzzy-match-name->license-ids "JSON License")))
    (is (= #{"LGPL-2.0"}                           (fuzzy-match-name->license-ids "GNU Library General Public License")))
    (is (= #{"LGPL-2.1"}                           (fuzzy-match-name->license-ids "GNU Lesser General Public License (LGPL)")))
    (is (= #{"LGPL-2.1"}                           (fuzzy-match-name->license-ids "GNU Lesser General Public License")))
    (is (= #{"MIT"}                                (fuzzy-match-name->license-ids "MIT License")))
    (is (= #{"MIT"}                                (fuzzy-match-name->license-ids "MIT license")))     ; Test capitalisation
    (is (= #{"MIT"}                                (fuzzy-match-name->license-ids "The MIT License")))
    (is (= #{"MPL-1.0"}                            (fuzzy-match-name->license-ids "Mozilla Public License")))
    (is (= #{"MPL-2.0"}                            (fuzzy-match-name->license-ids "Mozilla Public License Version 2.0")))
    (is (= #{"Plexus"}                             (fuzzy-match-name->license-ids "Similar to Apache License but with the acknowledgment clause removed"))))   ; JDOM - see https://lists.linuxfoundation.org/pipermail/spdx-legal/2014-December/001280.html
  (testing "Names that appear in licensey things, but are ambiguous"
    (is (nil?                                      (fuzzy-match-name->license-ids "BSD"))))
  (testing "Names that appear in licensey things, but aren't in the SPDX license list, and don't have identified SPDX identifiers"
    (is (= #{"LicenseRef-lice-comb-public-domain"} (fuzzy-match-name->license-ids "Public Domain")))
    (is (= #{"LicenseRef-lice-comb-public-domain"} (fuzzy-match-name->license-ids "Public domain")))))

(deftest uri->license-ids-tests
  (testing "Nil, empty or blank uri"
    (is (nil?                                 (fuzzy-match-uri->license-ids nil)))
    (is (nil?                                 (fuzzy-match-uri->license-ids "")))
    (is (nil?                                 (fuzzy-match-uri->license-ids "       ")))
    (is (nil?                                 (fuzzy-match-uri->license-ids "\n")))
    (is (nil?                                 (fuzzy-match-uri->license-ids "\t"))))
  (testing "URIs that appear verbatim in the SPDX license list"
    (is (= "Apache-2.0"                       (fuzzy-match-uri->license-ids "https://www.apache.org/licenses/LICENSE-2.0")))
    (is (= "Apache-2.0"                       (fuzzy-match-uri->license-ids "http://www.apache.org/licenses/LICENSE-2.0.html")))
    (is (= "Apache-2.0"                       (fuzzy-match-uri->license-ids "https://apache.org/licenses/LICENSE-2.0.txt")))
    (is (= "Apache-2.0"                       (fuzzy-match-uri->license-ids "               https://www.apache.org/licenses/LICENSE-2.0             ")))   ; Test whitespace
    (is (let [license-id (fuzzy-match-uri->license-ids "https://www.gnu.org/licenses/agpl.txt")]
          (or (= "AGPL-3.0"      license-id)
              (= "AGPL-3.0-only" license-id))))
    (is (= "CC-BY-SA-4.0"                     (fuzzy-match-uri->license-ids "https://creativecommons.org/licenses/by-sa/4.0/legalcode")))
    (is (= "GPL-2.0-with-classpath-exception" (fuzzy-match-uri->license-ids "https://www.gnu.org/software/classpath/license.html"))))
  (testing "URIs that appear in licensey things, but aren't in the SPDX license list"
    (is (= "Apache-2.0"                       (fuzzy-match-uri->license-ids "http://www.apache.org/licenses/LICENSE-2.0")))
    (is (= "Apache-2.0"                       (fuzzy-match-uri->license-ids "https://www.apache.org/licenses/LICENSE-2.0.txt")))))

(defn- string-text->ids
  [s]
  (with-open [is (io/input-stream (.getBytes s "UTF-8"))]
    (text->ids is)))

(deftest text->ids-tests
  (testing "Nil, empty or blank text"
    (is (nil?                                  (text->ids nil)))
    (is (nil?                                  (text->ids "")))
    (is (nil?                                  (text->ids "       ")))
    (is (nil?                                  (text->ids "\n")))
    (is (nil?                                  (text->ids "\t")))
    (is (thrown? java.io.FileNotFoundException (text->ids (io/file ""))))
    (is (thrown? java.io.FileNotFoundException (text->ids (io/file "       "))))
    (is (thrown? java.io.FileNotFoundException (text->ids (io/file "\n"))))
    (is (thrown? java.io.FileNotFoundException (text->ids (io/file "\t")))))
  (testing "Text"
    (is (= #{"Apache-2.0"}   (string-text->ids "Apache License\nVersion 2.0, January 2004")))
    (is (= #{"Apache-2.0"}   (string-text->ids "               Apache License\n               Version 2.0, January 2004             ")))
    (is (= #{"AGPL-3.0"}     (string-text->ids "GNU AFFERO GENERAL PUBLIC LICENSE\nVersion 3, 19 November 2007")))
    (is (= #{"CC-BY-SA-4.0"} (string-text->ids "Creative Commons Attribution-ShareAlike\n4.0 International Public License")))
    (is (= #{"JSON"}         (string-text->ids "Copyright (c) 2002 JSON.org")))))
