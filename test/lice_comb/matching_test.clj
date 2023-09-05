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

(ns lice-comb.matching-test
  (:require [clojure.test               :refer [deftest testing is use-fixtures]]
            [lice-comb.test-boilerplate :refer [fixture valid= valid-info=]]
            [lice-comb.impl.spdx        :as lcis]
            [lice-comb.matching         :refer [init! unlisted? proprietary-commercial? text->ids name->expressions name->expressions-info uri->ids]]
            [spdx.licenses              :as sl]
            [spdx.exceptions            :as se]))

(use-fixtures :once fixture)

(defn unlisted-only?
  "Does the given set of ids contain only a single unlisted license?"
  [ids]
  (and (= 1 (count ids))
       (unlisted? (first ids))))

(deftest init!-tests
  (testing "Nil response"
    (is (nil? (init!)))))

(deftest unlisted?-tests
  (testing "Nil, empty or blank ids"
    (is (nil?   (unlisted? nil)))
    (is (false? (unlisted? "")))
    (is (false? (unlisted? "       ")))
    (is (false? (unlisted? "\n")))
    (is (false? (unlisted? "\t"))))
  (testing "Unlisted ids"
    (is (true?  (unlisted? (lcis/name->unlisted "foo")))))
  (testing "Listed ids"
    (is (true?  (every? false? (map unlisted? (sl/ids)))))
    (is (true?  (every? false? (map unlisted? (se/ids)))))))

(deftest name->expressions-tests
  (testing "Nil, empty or blank"
    (is (nil?                                           (name->expressions nil)))
    (is (nil?                                           (name->expressions "")))
    (is (nil?                                           (name->expressions "       ")))
    (is (nil?                                           (name->expressions "\n")))
    (is (nil?                                           (name->expressions "\t"))))
  (testing "SPDX license ids"
    (is (valid= #{"AGPL-3.0-only"}                      (name->expressions "AGPL-3.0")))
    (is (valid= #{"AGPL-3.0-only"}                      (name->expressions "AGPL-3.0-only")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "    Apache-2.0        ")))   ; Test whitespace
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache-2.0")))
    (is (valid= #{"CC-BY-SA-4.0"}                       (name->expressions "CC-BY-SA-4.0")))
    (is (valid= #{"GPL-2.0-only"}                       (name->expressions "GPL-2.0")))
    (is (valid= #{"GPL-2.0-only WITH Classpath-exception-2.0"} (name->expressions "GPL-2.0-with-classpath-exception"))))
  (testing "Public domain and proprietary/commercial"
    (is (valid= #{(lcis/public-domain)}                 (name->expressions "Public Domain")))
    (is (valid= #{(lcis/public-domain)}                 (name->expressions "Public domain")))  ; Test lower case
    (is (valid= #{(lcis/public-domain)}                 (name->expressions "              Public domain   ")))  ; Test whitespace
    (is (valid= #{(lcis/proprietary-commercial)}        (name->expressions "Proprietary")))
    (is (valid= #{(lcis/proprietary-commercial)}        (name->expressions "Commercial")))
    (is (valid= #{(lcis/proprietary-commercial)}        (name->expressions "All rights reserved"))))
  (testing "SPDX expressions"
    (is (valid= #{"GPL-2.0-only WITH Classpath-exception-2.0"} (name->expressions "GPL-2.0 WITH Classpath-exception-2.0")))
    (is (valid= #{"Apache-2.0 OR GPL-3.0-only"}         (name->expressions "Apache-2.0 OR GPL-3.0")))
    (is (valid= #{"EPL-2.0 OR GPL-2.0-or-later WITH Classpath-exception-2.0 OR MIT OR (BSD-3-Clause AND Apache-2.0)"} (name->expressions "EPL-2.0 OR (GPL-2.0+ WITH Classpath-exception-2.0) OR MIT OR (BSD-3-Clause AND Apache-2.0)"))))
  (testing "Single expressions that are not valid SPDX"
    (is (valid= #{"GPL-2.0-only WITH Classpath-exception-2.0"} (name->expressions "GNU General Public License, version 2 with the GNU Classpath Exception")))
    (is (valid= #{"Apache-2.0 OR GPL-3.0-only"}         (name->expressions "Apache License version 2.0 or GNU General Public License version 3")))
    (is (valid= #{"EPL-2.0 OR GPL-2.0-or-later WITH Classpath-exception-2.0 OR MIT OR (BSD-3-Clause AND Apache-2.0)"} (name->expressions "EPL-2.0 OR (GPL-2.0+ WITH Classpath-exception-2.0) OR MIT OR (BSD-3-Clause AND Apache-2.0)")))
    (is (valid= #{"Apache-2.0 AND MIT"}                 (name->expressions "Apache & MIT licence")))
    (is (valid= #{"CDDL-1.1"}                           (name->expressions "Common Development and Distribution Licence"))))
  (testing "Expressions with weird operators"
    (is (valid= #{"Apache-2.0"}                         (name->expressions "and and and Apache License 2.0")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache Licence 2.0 or or or")))
    (is (valid= #{"Apache-2.0 OR MIT"}                  (name->expressions "Apache License 2.0 or or or or or or or or MIT license")))
    (is (valid= #{"Apache-2.0" "MIT"}                   (name->expressions "Apache License 2.0 or and or and or and or and MIT license")))
    (is (valid= #{"Apache-2.0" "MIT"}                   (name->expressions "or and Apache Licence 2.0 or and or and or and or and MIT and or and")))
    (is (valid= #{"Apache-2.0" "MIT"}                   (name->expressions "Apache License 2.0 and/or MIT licence"))))
  (testing "Multiple expressions"
    (is (valid= #{"MIT" "BSD-4-Clause"}                 (name->expressions "MIT / BSD")))
    (is (valid= #{"Apache-2.0" "GPL-3.0-only"}          (name->expressions "Apache License version 2.0 / GNU General Public License version 3")))
    (is (valid= #{"Apache-2.0" "GPL-3.0-only WITH Classpath-exception-2.0"} (name->expressions "Apache License version 2.0 / GNU General Public License version 3 with classpath exception")))
    (is (valid= #{"EPL-2.0 OR GPL-2.0-or-later WITH Classpath-exception-2.0 OR MIT OR BSD-3-Clause AND Apache-2.0"} (name->expressions "Eclipse Public License or General Public License 2.0 or (at your discretion) later w/ classpath exception or MIT Licence or three clause bsd and Apache Licence"))))
  (testing "Messed up license expressions"
    (is (valid= #{"Apache-2.0" "MIT"}                   (name->expressions "Apache with MIT"))))
  (testing "Names seen in handpicked POMs on Maven Central"
    (is (valid= #{"AGPL-3.0-only"}                      (name->expressions "GNU Affero General Public License (AGPL) version 3.0")))
    (is (valid= #{"AGPL-3.0-only"}                      (name->expressions "GNU Affero General Public License v3.0 only")))
    (is (valid= #{"AGPL-3.0-only"}                      (name->expressions "GNU Affero General Public License v3.0")))
    (is (valid= #{"Apache-1.0"}                         (name->expressions "Apache License 1")))
    (is (valid= #{"Apache-1.0"}                         (name->expressions "Apache License 1.0")))
    (is (valid= #{"Apache-1.0"}                         (name->expressions "Apache License Version 1.0")))
    (is (valid= #{"Apache-1.0"}                         (name->expressions "Apache License, Version 1.0")))
    (is (valid= #{"Apache-1.0"}                         (name->expressions "Apache Software License - Version 1.0")))
    (is (valid= #{"Apache-1.1"}                         (name->expressions "Apache License 1.1")))
    (is (valid= #{"Apache-1.1"}                         (name->expressions "Apache License Version 1.1")))
    (is (valid= #{"Apache-1.1"}                         (name->expressions "Apache License, Version 1.1")))
    (is (valid= #{"Apache-1.1"}                         (name->expressions "Apache Software License - Version 1.1")))
    (is (valid= #{"Apache-1.1"}                         (name->expressions "The MX4J License, version 1.0")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "               Apache Software License, Version 2.0             ")))   ; Test whitespace
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache 2")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache 2.0")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache License 2.0")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache License Version 2.0")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache License, Version 2.0")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache Software License - Version 2.0")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache Software License 2")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache Software License 2.0")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache Software License Version 2")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache Software License Version 2.0")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache Software License v2")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache Software License v2.0")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache Software License")))  ; Listed license missing version - we assume the latest
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache Software License, Version 2.0")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache v2")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "The Apache Software License, Version 2.0")))
    (is (valid= #{"BSD-3-Clause"}                       (name->expressions "3-Clause BSD License")))
    (is (valid= #{"BSD-3-Clause"}                       (name->expressions "BSD 3-Clause License")))
    (is (valid= #{"BSD-3-Clause"}                       (name->expressions "The BSD 3-Clause License (BSD3)")))
    (is (valid= #{"BSD-3-Clause-Attribution"}           (name->expressions "BSD 3-Clause Attribution")))
    (is (valid= #{"BSD-4-Clause"}                       (name->expressions "BSD")))
    (is (valid= #{"CC-BY-3.0"}                          (name->expressions "Attribution 3.0 Unported")))
    (is (valid= #{"CC-BY-3.0"}                          (name->expressions "Creative Commons Legal Code Attribution 3.0 Unported")))
    (is (valid= #{"CC-BY-4.0"}                          (name->expressions "Attribution 4.0 International")))
    (is (valid= #{"CC-BY-SA-4.0"}                       (name->expressions "Creative Commons Attribution Share Alike 4.0 International")))
    (is (valid= #{"CDDL-1.0"}                           (name->expressions "COMMON DEVELOPMENT AND DISTRIBUTION LICENSE (CDDL) Version 1.0")))
    (is (valid= #{"CDDL-1.0"}                           (name->expressions "COMMON DEVELOPMENT AND DISTRIBUTION LICENSE Version 1")))
    (is (valid= #{"CDDL-1.0"}                           (name->expressions "COMMON DEVELOPMENT AND DISTRIBUTION LICENSE Version 1.0")))
    (is (valid= #{"CDDL-1.1"}                           (name->expressions "COMMON DEVELOPMENT AND DISTRIBUTION LICENSE (CDDL) Version 1.1")))
    (is (valid= #{"CDDL-1.1"}                           (name->expressions "COMMON DEVELOPMENT AND DISTRIBUTION LICENSE Version 1.1")))
    (is (valid= #{"EPL-1.0"}                            (name->expressions "Eclipse Public License - v 1.0")))
    (is (valid= #{"EPL-1.0"}                            (name->expressions "Eclipse Public License 1.0")))
    (is (valid= #{"EPL-1.0"}                            (name->expressions "Eclipse Public License, Version 1.0")))
    (is (valid= #{"EPL-2.0"}                            (name->expressions "Eclipse Public License (EPL)")))  ; Listed license missing version - we assume the latest
    (is (valid= #{"EPL-2.0"}                            (name->expressions "Eclipse Public License 2.0")))
    (is (valid= #{"EPL-2.0"}                            (name->expressions "Eclipse Public License version 2")))
    (is (valid= #{"EPL-2.0"}                            (name->expressions "Eclipse Public License")))  ; Listed license missing version - we assume the latest
    (is (valid= #{"EPL-2.0"}                            (name->expressions "Eclipse Public License")))  ; Listed license missing version - we assume the latest
    (is (valid= #{"GPL-2.0-only WITH Classpath-exception-2.0"} (name->expressions "GNU General Public License v2.0 w/Classpath exception")))
    (is (valid= #{"GPL-2.0-only WITH Classpath-exception-2.0"} (name->expressions "GNU General Public License, version 2 (GPL2), with the classpath exception")))
    (is (valid= #{"GPL-2.0-only WITH Classpath-exception-2.0"} (name->expressions "GNU General Public License, version 2 with the GNU Classpath Exception")))
    (is (valid= #{"GPL-2.0-only WITH Classpath-exception-2.0"} (name->expressions "GPLv2+CE")))  ;#### !!!!
    (is (valid= #{"GPL-2.0-only"}                       (name->expressions "GNU General Public License, version 2")))
    (is (valid= #{"JSON"}                               (name->expressions "JSON License")))
    (is (valid= #{"LGPL-3.0-only"}                      (name->expressions "GNU Lesser General Public License (LGPL)")))  ; Listed license missing version - we assume the latest
    (is (valid= #{"LGPL-3.0-only"}                      (name->expressions "GNU Lesser General Public License")))  ; Listed license missing version - we assume the latest
    (is (valid= #{"LGPL-3.0-only"}                      (name->expressions "GNU Library General Public License")))  ; Listed license missing version - we assume the latest
    (is (valid= #{"MIT"}                                (name->expressions "Bouncy Castle Licence")))  ; Note spelling of "licence"
    (is (valid= #{"MIT"}                                (name->expressions "MIT License")))
    (is (valid= #{"MIT"}                                (name->expressions "MIT license")))     ; Test capitalisation
    (is (valid= #{"MIT"}                                (name->expressions "The MIT License")))
    (is (valid= #{"MPL-1.0"}                            (name->expressions "Mozilla Public License 1")))
    (is (valid= #{"MPL-2.0"}                            (name->expressions "Mozilla Public License Version 2.0")))
    (is (valid= #{"MPL-2.0"}                            (name->expressions "Mozilla Public License")))  ; Listed license missing version - we assume the latest
    (is (valid= #{"Plexus"}                             (name->expressions "Similar to Apache License but with the acknowledgment clause removed"))))   ; JDOM - see https://lists.linuxfoundation.org/pipermail/spdx-legal/2014-December/001280.html
  (testing "All names seen in POMs on Clojars as of 2023-07-13"
    (is (valid= #{"AFL-3.0"}                            (name->expressions "Academic Free License 3.0")))
    (is (valid= #{"AGPL-3.0-only" (lcis/proprietary-commercial)} (name->expressions "GNU Affero General Public License Version 3; Other commercial licenses available.")))
    (is (valid= #{"AGPL-3.0-only"}                      (name->expressions "AGPL v3")))
    (is (valid= #{"AGPL-3.0-only"}                      (name->expressions "AGPL")))  ; Listed license missing version - we assume the latest
    (is (valid= #{"AGPL-3.0-only"}                      (name->expressions "AGPLv3")))
    (is (valid= #{"AGPL-3.0-only"}                      (name->expressions "Affero GNU Public License v3")))  ; Listed license missing version - we assume the latest
    (is (valid= #{"AGPL-3.0-only"}                      (name->expressions "Affero General Public License")))
    (is (valid= #{"AGPL-3.0-only"}                      (name->expressions "Affero General Public License,")))  ; Listed license missing version - we assume the latest
    (is (valid= #{"AGPL-3.0-only"}                      (name->expressions "GNU AFFERO GENERAL PUBLIC LICENSE Version 3")))
    (is (valid= #{"AGPL-3.0-only"}                      (name->expressions "GNU AFFERO GENERAL PUBLIC LICENSE, Version 3")))
    (is (valid= #{"AGPL-3.0-only"}                      (name->expressions "GNU AGPLv3")))
    (is (valid= #{"AGPL-3.0-only"}                      (name->expressions "GNU Affero General Public Licence")))  ; Listed license missing version - we assume the latest
    (is (valid= #{"AGPL-3.0-only"}                      (name->expressions "GNU Affero General Public License (AGPL)")))  ; Listed license missing version - we assume the latest
    (is (valid= #{"AGPL-3.0-only"}                      (name->expressions "GNU Affero General Public License 3.0 (AGPL-3.0)")))
    (is (valid= #{"AGPL-3.0-only"}                      (name->expressions "GNU Affero General Public License Version 3")))
    (is (valid= #{"AGPL-3.0-only"}                      (name->expressions "GNU Affero General Public License v3")))
    (is (valid= #{"AGPL-3.0-only"}                      (name->expressions "GNU Affero General Public License v3.0")))
    (is (valid= #{"AGPL-3.0-only"}                      (name->expressions "GNU Affero General Public License")))  ; Listed license missing version - we assume the latest
    (is (valid= #{"AGPL-3.0-only"}                      (name->expressions "GNU Affero General Public License, Version 3")))
    (is (valid= #{"AGPL-3.0-only"}                      (name->expressions "GNU Affero General Public License, version 3")))
    (is (valid= #{"AGPL-3.0-or-later"}                  (name->expressions "Affero General Public License v3 or later (at your option)")))
    (is (valid= #{"AGPL-3.0-or-later"}                  (name->expressions "Affero General Public License version 3 or lator")))  ; Typo in "lator"
    (is (valid= #{"AGPL-3.0-or-later"}                  (name->expressions "GNU AGPL-V3 or later")))
    (is (valid= #{"Apache-2.0 WITH LLVM-exception"}     (name->expressions "Apache 2.0 with LLVM Exception")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions " Apache License, Version 2.0")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "APACHE LICENSE, VERSION 2.0 (CURRENT)")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "APACHE LICENSE, VERSION 2.0")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "APACHE")))  ; Listed license missing version - we assume the latest
    (is (valid= #{"Apache-2.0"}                         (name->expressions "ASL 2.0")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "ASL")))  ; Listed license missing version - we assume the latest
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache 2 License")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache 2 Public License")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache 2")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache 2, see LICENSE")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache 2.0 License")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache 2.0")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache Licence 2.0")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache Licence")))  ; Listed license missing clause info
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache Licence, Version 2.0")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache License - Version 2.0")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache License - v 2.0")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache License - v2.0")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache License 2")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache License 2.0")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache License V2")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache License V2.0")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache License Version 2.0")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache License Version 2.0")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache License Version 2.0, January 2004")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache License v 2.0")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache License v2")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache License v2.0")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache License version 2.0")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache License")))  ; Listed license missing clause info
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache License, 2.0")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache License, Version 2.0")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache License, Version 2.0.")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache License, version 2.")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache License, version 2.0")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache Public License 2.0")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache Public License v2")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache Public License")))  ; Listed license missing clause info
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache Public License, Version 2.0")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache Public License, version 2.0")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache Software License - v 2.0")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache Software License 2.0")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache Software License")))  ; Listed license missing clause info
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache Software License, Version 2.0")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache Software Licesne")))  ; Listed license missing clause info
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache Sofware Licencse 2.0")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache Sofware License 2.0")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache V2 License")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache V2")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache Version 2.0")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache license version 2")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache license, Version 2.0")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache v2 License")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache v2")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache v2.0")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache")))  ; Listed license missing clause info
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache, Version 2.0")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache-2.0 License")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache-2.0")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "Apache2 License")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "The Apache 2 License")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "The Apache License, Version 2.0")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "The Apache Software License, Version 2.0")))
    (is (valid= #{"Apache-2.0"}                         (name->expressions "apache")))  ; Listed license missing version - we assume the latest
    (is (valid= #{"Apache-2.0"}                         (name->expressions "apache-2.0")))
    (is (valid= #{"Artistic-2.0" "GPL-3.0-only"}        (name->expressions "Artistic License/GPL")))  ; Missing conjunction, so return 2 (singleton) expressions
    (is (valid= #{"Artistic-2.0"}                       (name->expressions "Artistic License")))  ; Listed license missing version - we assume the latest
    (is (valid= #{"Artistic-2.0"}                       (name->expressions "Artistic-2.0")))
    (is (valid= #{"BSD-2-Clause"}                       (name->expressions "2-Clause BSD License")))
    (is (valid= #{"BSD-2-Clause"}                       (name->expressions "2-Clause BSD")))
    (is (valid= #{"BSD-2-Clause"}                       (name->expressions "BSD (2 Clause)")))
    (is (valid= #{"BSD-2-Clause"}                       (name->expressions "BSD (2-Clause)")))
    (is (valid= #{"BSD-2-Clause"}                       (name->expressions "BSD (Type 2) Public License")))
    (is (valid= #{"BSD-2-Clause"}                       (name->expressions "BSD 2 Clause")))
    (is (valid= #{"BSD-2-Clause"}                       (name->expressions "BSD 2 clause license")))
    (is (valid= #{"BSD-2-Clause"}                       (name->expressions "BSD 2")))
    (is (valid= #{"BSD-2-Clause"}                       (name->expressions "BSD 2-Clause Licence")))
    (is (valid= #{"BSD-2-Clause"}                       (name->expressions "BSD 2-Clause License")))
    (is (valid= #{"BSD-2-Clause"}                       (name->expressions "BSD 2-Clause \"Simplified\" License")))
    (is (valid= #{"BSD-2-Clause"}                       (name->expressions "BSD 2-Clause license")))
    (is (valid= #{"BSD-2-Clause"}                       (name->expressions "BSD 2-Clause")))
    (is (valid= #{"BSD-2-Clause"}                       (name->expressions "BSD 2-clause \"Simplified\" License")))
    (is (valid= #{"BSD-2-Clause"}                       (name->expressions "BSD C2")))
    (is (valid= #{"BSD-2-Clause"}                       (name->expressions "BSD-2-Clause")))
    (is (valid= #{"BSD-2-Clause"}                       (name->expressions "New BSD 2-clause license")))
    (is (valid= #{"BSD-2-Clause"}                       (name->expressions "Simplified BSD License")))
    (is (valid= #{"BSD-2-Clause"}                       (name->expressions "Simplified BSD license")))
    (is (valid= #{"BSD-2-Clause"}                       (name->expressions "The BSD 2-Clause License")))
    (is (valid= #{"BSD-2-Clause"}                       (name->expressions "Two clause BSD license")))
    (is (valid= #{"BSD-2-Clause-FreeBSD"}               (name->expressions "FreeBSD License")))
    (is (valid= #{"BSD-3-Clause" "MIT"}                 (name->expressions "New-BSD / MIT")))  ; Missing conjunction, so return 2 (singleton) expressions
    (is (valid= #{"BSD-3-Clause"}                       (name->expressions "3-Clause BSD License")))
    (is (valid= #{"BSD-3-Clause"}                       (name->expressions "3-Clause BSD")))
    (is (valid= #{"BSD-3-Clause"}                       (name->expressions "3-clause BSD licence (Revised BSD licence), also included in the jar file")))
    (is (valid= #{"BSD-3-Clause"}                       (name->expressions "3-clause BSD license")))
    (is (valid= #{"BSD-3-Clause"}                       (name->expressions "3-clause license (New BSD License or Modified BSD License)")))
    (is (valid= #{"BSD-3-Clause"}                       (name->expressions "Aduna BSD license")))
    (is (valid= #{"BSD-3-Clause"}                       (name->expressions "BSD 3 Clause")))
    (is (valid= #{"BSD-3-Clause"}                       (name->expressions "BSD 3-Clause 'New' or 'Revised' License")))
    (is (valid= #{"BSD-3-Clause"}                       (name->expressions "BSD 3-Clause License")))
    (is (valid= #{"BSD-3-Clause"}                       (name->expressions "BSD 3-Clause \"New\" or \"Revised\" License")))
    (is (valid= #{"BSD-3-Clause"}                       (name->expressions "BSD 3-Clause license")))
    (is (valid= #{"BSD-3-Clause"}                       (name->expressions "BSD 3-Clause")))
    (is (valid= #{"BSD-3-Clause"}                       (name->expressions "BSD 3-clause License")))
    (is (valid= #{"BSD-3-Clause"}                       (name->expressions "BSD 3-clause license")))
    (is (valid= #{"BSD-3-Clause"}                       (name->expressions "BSD 3-clause")))
    (is (valid= #{"BSD-3-Clause"}                       (name->expressions "BSD New, Version 3.0")))
    (is (valid= #{"BSD-3-Clause"}                       (name->expressions "BSD-3")))
    (is (valid= #{"BSD-3-Clause"}                       (name->expressions "BSD-3-Clause")))
    (is (valid= #{"BSD-3-Clause"}                       (name->expressions "Modified BSD License")))
    (is (valid= #{"BSD-3-Clause"}                       (name->expressions "New BSD License or Modified BSD License")))
    (is (valid= #{"BSD-3-Clause"}                       (name->expressions "New BSD License")))
    (is (valid= #{"BSD-3-Clause"}                       (name->expressions "New BSD license")))
    (is (valid= #{"BSD-3-Clause"}                       (name->expressions "Revised BSD")))
    (is (valid= #{"BSD-3-Clause"}                       (name->expressions "The 3-Clause BSD License")))
    (is (valid= #{"BSD-3-Clause"}                       (name->expressions "The BSD 3-Clause License")))
    (is (valid= #{"BSD-3-Clause"}                       (name->expressions "The New BSD License")))
    (is (valid= #{"BSD-3-Clause"}                       (name->expressions "The New BSD license")))
    (is (valid= #{"BSD-3-Clause"}                       (name->expressions "Three Clause BSD-like License")))
;    (is (valid= #{"BSD-3-Clause"}                       (name->expressions "https://github.com/mixradio/clafka/blob/master/LICENSE")))                           ; Failing due to https://github.com/spdx/Spdx-Java-Library/issues/182
;    (is (valid= #{"BSD-3-Clause"}                       (name->expressions "https://github.com/mixradio/faraday-atom/blob/master/LICENSE")))                     ; Failing due to https://github.com/spdx/Spdx-Java-Library/issues/182
;    (is (valid= #{"BSD-3-Clause"}                       (name->expressions "https://github.com/mixradio/graphite-filter/blob/master/LICENSE")))                  ; Failing due to https://github.com/spdx/Spdx-Java-Library/issues/182
;    (is (valid= #{"BSD-3-Clause"}                       (name->expressions "https://github.com/mixradio/instrumented-ring-jetty-adapter/blob/master/LICENSE")))  ; Failing due to https://github.com/spdx/Spdx-Java-Library/issues/182
;    (is (valid= #{"BSD-3-Clause"}                       (name->expressions "https://github.com/mixradio/mr-clojure/blob/master/LICENSE")))                       ; Failing due to https://github.com/spdx/Spdx-Java-Library/issues/182
;    (is (valid= #{"BSD-3-Clause"}                       (name->expressions "https://github.com/mixradio/mr-edda/blob/master/LICENSE")))                          ; Failing due to https://github.com/spdx/Spdx-Java-Library/issues/182
;    (is (valid= #{"BSD-3-Clause"}                       (name->expressions "https://github.com/mixradio/multi-atom/blob/master/LICENSE")))                       ; Failing due to https://github.com/spdx/Spdx-Java-Library/issues/182
;    (is (valid= #{"BSD-3-Clause"}                       (name->expressions "https://github.com/mixradio/party/blob/master/LICENSE")))                            ; Failing due to https://github.com/spdx/Spdx-Java-Library/issues/182
;    (is (valid= #{"BSD-3-Clause"}                       (name->expressions "https://github.com/mixradio/radix/blob/master/LICENSE")))                            ; Failing due to https://github.com/spdx/Spdx-Java-Library/issues/182
;    (is (valid= #{"BSD-3-Clause"}                       (name->expressions "https://github.com/riverford/datagrep/blob/master/LICENSE")))                        ; Failing due to https://github.com/spdx/Spdx-Java-Library/issues/182
;    (is (valid= #{"BSD-3-Clause"}                       (name->expressions "https://github.com/riverford/durable-ref/blob/master/LICENSE")))                     ; Failing due to https://github.com/spdx/Spdx-Java-Library/issues/182
;    (is (valid= #{"BSD-3-Clause"}                       (name->expressions "https://github.com/smsharman/sxm-clojure-ms/blob/master/LICENSE")))                  ; Failing due to https://github.com/spdx/Spdx-Java-Library/issues/182
    (is (valid= #{"BSD-3-Clause"}                       (name->expressions "https://opensource.org/licenses/BSD-3-Clause")))
    (is (valid= #{"BSD-3-Clause"}                       (name->expressions "new BSD License")))
    (is (valid= #{"BSD-4-Clause"}                       (name->expressions "BSD License")))  ; Listed license missing clause info - we assume original (4 clause)
    (is (valid= #{"BSD-4-Clause"}                       (name->expressions "BSD Standard License")))  ; Listed license missing clause info - we assume original (4 clause)
    (is (valid= #{"BSD-4-Clause"}                       (name->expressions "BSD license")))  ; Listed license missing clause info - we assume original (4 clause)
    (is (valid= #{"BSD-4-Clause"}                       (name->expressions "BSD")))  ; Listed license missing clause info - we assume original (4 clause)
    (is (valid= #{"BSD-4-Clause"}                       (name->expressions "BSD-style")))  ; Listed license missing clause info - we assume original (4 clause)
    (is (valid= #{"BSD-4-Clause"}                       (name->expressions "The BSD License")))
    (is (valid= #{"BSL-1.0"}                            (name->expressions "Boost Software License - Version 1.0")))
    (is (valid= #{"Beerware"}                           (name->expressions "Beerware 42")))
    (is (valid= #{"Beerware"}                           (name->expressions "THE BEER-WARE LICENSE")))
    (is (valid= #{"CC-BY-2.5"}                          (name->expressions "Creative Commons Attribution 2.5 License")))
    (is (valid= #{"CC-BY-3.0"}                          (name->expressions "Creative Commons 3.0")))
    (is (valid= #{"CC-BY-4.0" (lcis/name->unlisted "exception for binary distribution")} (name->expressions "CC Attribution 4.0 International with exception for binary distribution")))  ; The exception in this case doesn't map to any listed SPDX identifier (including CC-BY variants)
    (is (valid= #{"CC-BY-4.0"}                          (name->expressions "CC-BY-4.0")))
    (is (valid= #{"CC-BY-4.0"}                          (name->expressions "Creative Commons Attribution License")))  ; Listed license missing version - we assume the latest
    (is (valid= #{"CC-BY-NC-3.0"}                       (name->expressions "Creative Commons Attribution-NonCommercial 3.0")))
    (is (valid= #{"CC-BY-NC-4.0"}                       (name->expressions "CC BY-NC")))  ; Listed license missing version - we assume the latest
    (is (valid= #{"CC-BY-NC-ND-3.0"}                    (name->expressions "Attribution-NonCommercial-NoDerivs 3.0 Unported")))
    (is (valid= #{"CC-BY-SA-3.0"}                       (name->expressions "Creative Commons Attribution-ShareAlike 3.0 US (CC-SA) license")))  ; Note: the US suffix here is meaningless, as there is no CC-BY-SA-3.0-US license id
    (is (valid= #{"CC-BY-SA-3.0"}                       (name->expressions "Creative Commons Attribution-ShareAlike 3.0 US (CC-SA)")))  ; Note: the US suffix here is meaningless, as there is no CC-BY-SA-3.0-US license id
    (is (valid= #{"CC-BY-SA-3.0"}                       (name->expressions "Creative Commons Attribution-ShareAlike 3.0 Unported License")))
    (is (valid= #{"CC-BY-SA-3.0"}                       (name->expressions "Creative Commons Attribution-ShareAlike 3.0 Unported")))
    (is (valid= #{"CC-BY-SA-3.0"}                       (name->expressions "Creative Commons Attribution-ShareAlike 3.0")))
    (is (valid= #{"CC-BY-SA-4.0"}                       (name->expressions "CC BY-SA 4.0")))
    (is (valid= #{"CC0-1.0"}                            (name->expressions "CC0 1.0 Universal (CC0 1.0) Public Domain Dedication")))
    (is (valid= #{"CC0-1.0"}                            (name->expressions "CC0 1.0 Universal")))
    (is (valid= #{"CC0-1.0"}                            (name->expressions "CC0")))
    (is (valid= #{"CC0-1.0"}                            (name->expressions "Public domain (CC0)")))
    (is (valid= #{"CDDL-1.1"}                           (name->expressions "Common Development and Distribution License (CDDL)")))  ; Listed license missing clause info
    (is (valid= #{"CDDL-1.1"}                           (name->expressions "Common Development and Distribution License")))  ; Listed license missing clause info
    (is (valid= #{"CECILL-2.1"}                         (name->expressions "CeCILL License")))  ; Listed license missing version - we assume the latest
    (is (valid= #{"CPL-1.0"}                            (name->expressions "Common Public License - v 1.0")))
    (is (valid= #{"CPL-1.0"}                            (name->expressions "Common Public License Version 1.0")))
    (is (valid= #{"EPL-1.0"}                            (name->expressions "EPL 1.0")))
    (is (valid= #{"EPL-1.0"}                            (name->expressions "EPL-1.0")))
    (is (valid= #{"EPL-1.0"}                            (name->expressions "EPL-v1.0")))
    (is (valid= #{"EPL-1.0"}                            (name->expressions "Eclipse Public License (EPL) - v 1.0")))
    (is (valid= #{"EPL-1.0"}                            (name->expressions "Eclipse Public License - Version 1.0")))
    (is (valid= #{"EPL-1.0"}                            (name->expressions "Eclipse Public License - v 1.0")))
    (is (valid= #{"EPL-1.0"}                            (name->expressions "Eclipse Public License - v1.0")))
    (is (valid= #{"EPL-1.0"}                            (name->expressions "Eclipse Public License 1.0 (EPL-1.0)")))
    (is (valid= #{"EPL-1.0"}                            (name->expressions "Eclipse Public License 1.0")))
    (is (valid= #{"EPL-1.0"}                            (name->expressions "Eclipse Public License v 1.0")))
    (is (valid= #{"EPL-1.0"}                            (name->expressions "Eclipse Public License v1.0")))
    (is (valid= #{"EPL-1.0"}                            (name->expressions "Eclipse Public License version 1.0")))
    (is (valid= #{"EPL-1.0"}                            (name->expressions "Eclipse Public License, version 1.0")))
    (is (valid= #{"EPL-1.0"}                            (name->expressions "Eclipse Public Licese - v 1.0")))
    (is (valid= #{"EPL-1.0"}                            (name->expressions "https://github.com/cmiles74/uio/blob/master/LICENSE")))
    (is (valid= #{"EPL-2.0 AND LGPL-3.0-only"}          (name->expressions "Dual: EPL and LGPL")))  ; Listed license missing version - we assume the latest
    (is (valid= #{"EPL-2.0 OR Apache-2.0"}              (name->expressions "Double licensed under the Eclipse Public License (the same as Clojure) or the Apache Public License 2.0.")))  ; Listed license missing version - we assume the latest
    (is (valid= #{"EPL-2.0 OR GPL-2.0-or-later WITH Classpath-exception-2.0"} (name->expressions "<script lang=\"javascript\">alert('hi');</script>EPL-2.0 OR GPL-2.0-or-later WITH Classpath-exception-2.0")))
    (is (valid= #{"EPL-2.0 OR GPL-2.0-or-later WITH Classpath-exception-2.0"} (name->expressions "EPL-2.0 OR GPL-2.0-or-later WITH Classpath Exception")))  ; Listed exception missing version - we assume the latest
    (is (valid= #{"EPL-2.0 OR GPL-2.0-or-later WITH Classpath-exception-2.0"} (name->expressions "EPL-2.0 OR GPL-2.0-or-later WITH Classpath-exception-2.0")))
    (is (valid= #{"EPL-2.0 OR GPL-2.0-or-later WITH Classpath-exception-2.0"} (name->expressions "Eclipse Public License 2.0 OR GNU GPL v2+ with Classpath exception")))
    (is (valid= #{"EPL-2.0 OR GPL-2.0-or-later"}        (name->expressions "EPL-2.0 OR GPL-2.0-or-later")))
    (is (valid= #{"EPL-2.0 OR GPL-3.0-or-later WITH Classpath-exception-2.0"} (name->expressions "EPL-2.0 OR GPL-3.0-or-later WITH Classpath-exception-2.0")))
    (is (valid= #{"EPL-2.0 OR GPL-3.0-or-later"}        (name->expressions "EPL-2.0 OR GPL-3.0-or-later")))
    (is (valid= #{"EPL-2.0" "MIT"}                      (name->expressions "Eclipse Public MIT")))  ; Listed license missing version - we assume the latest  ; Missing conjunction, so return 2 (singleton) expressions
    (is (valid= #{"EPL-2.0"}                            (name->expressions "Copyright (C) 2013 Mathieu Gauthron. Distributed under the Eclipse Public License.")))
    (is (valid= #{"EPL-2.0"}                            (name->expressions "Copyright (C) 2014 Mathieu Gauthron. Distributed under the Eclipse Public License.")))
    (is (valid= #{"EPL-2.0"}                            (name->expressions "Distributed under the Eclipse Public License, the same as Clojure.")))  ; Listed license missing version - we assume the latest
    (is (valid= #{"EPL-2.0"}                            (name->expressions "ECLIPSE PUBLIC LICENSE")))  ; Listed license missing version - we assume the latest
    (is (valid= #{"EPL-2.0"}                            (name->expressions "EPL")))  ; Listed license missing version - we assume the latest
    (is (valid= #{"EPL-2.0"}                            (name->expressions "EPL-2.0")))
    (is (valid= #{"EPL-2.0"}                            (name->expressions "EPLv2")))
    (is (valid= #{"EPL-2.0"}                            (name->expressions "Eclipse License")))  ; Listed license missing version - we assume the latest
    (is (valid= #{"EPL-2.0"}                            (name->expressions "Eclipse Public Licence")))  ; Listed license missing version - we assume the latest
    (is (valid= #{"EPL-2.0"}                            (name->expressions "Eclipse Public License (EPL)")))  ; Listed license missing version - we assume the latest
    (is (valid= #{"EPL-2.0"}                            (name->expressions "Eclipse Public License - v 2.0")))
    (is (valid= #{"EPL-2.0"}                            (name->expressions "Eclipse Public License 2")))
    (is (valid= #{"EPL-2.0"}                            (name->expressions "Eclipse Public License 2.0")))
    (is (valid= #{"EPL-2.0"}                            (name->expressions "Eclipse Public License 2.0,")))
    (is (valid= #{"EPL-2.0"}                            (name->expressions "Eclipse Public License v2.0")))
    (is (valid= #{"EPL-2.0"}                            (name->expressions "Eclipse Public License version 2")))
    (is (valid= #{"EPL-2.0"}                            (name->expressions "Eclipse Public License version 2.0")))
    (is (valid= #{"EPL-2.0"}                            (name->expressions "Eclipse Public License")))  ; Listed license missing version - we assume the latest
    (is (valid= #{"EPL-2.0"}                            (name->expressions "Eclipse Public License, v. 2.0")))
    (is (valid= #{"EPL-2.0"}                            (name->expressions "Eclipse Public License, v2")))
    (is (valid= #{"EPL-2.0"}                            (name->expressions "Eclipse Pulic License")))  ; Listed license missing version - we assume the latest
    (is (valid= #{"EPL-2.0"}                            (name->expressions "Eclipse public license, the same as Clojure")))
    (is (valid= #{"EPL-2.0"}                            (name->expressions "Eclipse")))  ; Listed license missing version - we assume the latest
    (is (valid= #{"EPL-2.0"}                            (name->expressions "Some Eclipse Public License")))  ; Listed license missing version - we assume the latest
    (is (valid= #{"EUPL-1.1"}                           (name->expressions "European Union Public Licence (EUPL v.1.1)")))
    (is (valid= #{"EUPL-1.1"}                           (name->expressions "The European Union Public License, Version 1.1")))
    (is (valid= #{"EUPL-1.2"}                           (name->expressions "European Union Public Licence v. 1.2")))
    (is (valid= #{"EUPL-1.2"}                           (name->expressions "European Union Public License 1.2 or later")))
    (is (valid= #{"EUPL-1.2"}                           (name->expressions "European Union Public License")))  ; Listed license missing version - we assume the latest
    (is (valid= #{"GPL-2.0-only WITH Classpath-exception-2.0"} (name->expressions "GNU General Public License, Version 2, with the Classpath Exception")))
    (is (valid= #{"GPL-2.0-only WITH Classpath-exception-2.0"} (name->expressions "GPLv2 with Classpath exception")))
    (is (valid= #{"GPL-2.0-only"}                       (name->expressions "GNU GENERAL PUBLIC LICENSE Version 2, June 1991")))
    (is (valid= #{"GPL-2.0-only"}                       (name->expressions "GNU General Public License 2")))
    (is (valid= #{"GPL-2.0-only"}                       (name->expressions "GNU General Public License, version 2")))
    (is (valid= #{"GPL-2.0-only"}                       (name->expressions "GNU Public License v2")))
    (is (valid= #{"GPL-2.0-only"}                       (name->expressions "GNU Public License, Version 2")))
    (is (valid= #{"GPL-2.0-only"}                       (name->expressions "GNU Public License, Version 2.0")))
    (is (valid= #{"GPL-2.0-only"}                       (name->expressions "GNU Public License, v2")))
    (is (valid= #{"GPL-2.0-only"}                       (name->expressions "GPL v2")))
    (is (valid= #{"GPL-2.0-only"}                       (name->expressions "GPL-2.0")))
    (is (valid= #{"GPL-2.0-only"}                       (name->expressions "GPLv2")))
    (is (valid= #{"GPL-2.0-only"}                       (name->expressions "The GNU General Public License, Version 2")))
    (is (valid= #{"GPL-2.0-or-later WITH Classpath-exception-2.0"} (name->expressions "GPL-2.0-or-later WITH Classpath-exception-2.0")))
    (is (valid= #{"GPL-2.0-or-later"}                   (name->expressions "GNU General Public License,version 2.0 or (at your option) any later version")))
    (is (valid= #{"GPL-2.0-or-later"}                   (name->expressions "GNU GPL V2+")))
    (is (valid= #{"GPL-2.0-or-later"}                   (name->expressions "GPL 2.0+")))
    (is (valid= #{"GPL-3.0-only"}                       (name->expressions " GNU GENERAL PUBLIC LICENSE Version 3")))
    (is (valid= #{"GPL-3.0-only"}                       (name->expressions "GNU GENERAL PUBLIC LICENSE")))  ; Listed license missing version - we assume the latest
    (is (valid= #{"GPL-3.0-only"}                       (name->expressions "GNU GPL 3")))
    (is (valid= #{"GPL-3.0-only"}                       (name->expressions "GNU GPL v 3.0")))
    (is (valid= #{"GPL-3.0-only"}                       (name->expressions "GNU GPL v. 3")))
    (is (valid= #{"GPL-3.0-only"}                       (name->expressions "GNU GPL v3")))
    (is (valid= #{"GPL-3.0-only"}                       (name->expressions "GNU GPL v3.0")))
    (is (valid= #{"GPL-3.0-only"}                       (name->expressions "GNU GPL")))  ; Listed license missing version - we assume the latest
    (is (valid= #{"GPL-3.0-only"}                       (name->expressions "GNU GPL, version 3, 29 June 2007")))
    (is (valid= #{"GPL-3.0-only"}                       (name->expressions "GNU General Public License (GPL)")))  ; Listed license missing version - we assume the latest
    (is (valid= #{"GPL-3.0-only"}                       (name->expressions "GNU General Public License V3")))
    (is (valid= #{"GPL-3.0-only"}                       (name->expressions "GNU General Public License Version 3")))
    (is (valid= #{"GPL-3.0-only"}                       (name->expressions "GNU General Public License v3")))
    (is (valid= #{"GPL-3.0-only"}                       (name->expressions "GNU General Public License v3.0")))
    (is (valid= #{"GPL-3.0-only"}                       (name->expressions "GNU General Public License")))  ; Listed license missing version - we assume the latest
    (is (valid= #{"GPL-3.0-only"}                       (name->expressions "GNU General Public License, Version 3")))
    (is (valid= #{"GPL-3.0-only"}                       (name->expressions "GNU General Public License, version 3 (GPLv3)")))
    (is (valid= #{"GPL-3.0-only"}                       (name->expressions "GNU General Public License, version 3")))
    (is (valid= #{"GPL-3.0-only"}                       (name->expressions "GNU Public License V. 3.0")))
    (is (valid= #{"GPL-3.0-only"}                       (name->expressions "GNU Public License V3")))
    (is (valid= #{"GPL-3.0-only"}                       (name->expressions "GNU Public License")))  ; Listed license missing version - we assume the latest
    (is (valid= #{"GPL-3.0-only"}                       (name->expressions "GNU public licence V3.0")))
    (is (valid= #{"GPL-3.0-only"}                       (name->expressions "GNU")))  ; Listed license missing version - we assume the latest
    (is (valid= #{"GPL-3.0-only"}                       (name->expressions "GNUv3")))
    (is (valid= #{"GPL-3.0-only"}                       (name->expressions "GPL 3")))
    (is (valid= #{"GPL-3.0-only"}                       (name->expressions "GPL 3.0")))
    (is (valid= #{"GPL-3.0-only"}                       (name->expressions "GPL V3")))
    (is (valid= #{"GPL-3.0-only"}                       (name->expressions "GPL v3")))
    (is (valid= #{"GPL-3.0-only"}                       (name->expressions "GPL version 3")))
    (is (valid= #{"GPL-3.0-only"}                       (name->expressions "GPL")))  ; Listed license missing version - we assume the latest
    (is (valid= #{"GPL-3.0-only"}                       (name->expressions "GPL-3")))
    (is (valid= #{"GPL-3.0-only"}                       (name->expressions "GPL-3.0")))
    (is (valid= #{"GPL-3.0-only"}                       (name->expressions "GPL-3.0-only")))
    (is (valid= #{"GPL-3.0-only"}                       (name->expressions "GPL3")))
    (is (valid= #{"GPL-3.0-only"}                       (name->expressions "GPLv3")))
    (is (valid= #{"GPL-3.0-only"}                       (name->expressions "General Public License 3")))
    (is (valid= #{"GPL-3.0-only"}                       (name->expressions "General Public License v3.0")))
    (is (valid= #{"GPL-3.0-only"}                       (name->expressions "The GNU General Public License v3.0")))
    (is (valid= #{"GPL-3.0-only"}                       (name->expressions "The GNU General Public License")))  ; Listed license missing version - we assume the latest
    (is (valid= #{"GPL-3.0-or-later"}                   (name->expressions "GNU GPL v3+")))
    (is (valid= #{"GPL-3.0-or-later"}                   (name->expressions "GNU GPLv3+")))
    (is (valid= #{"GPL-3.0-or-later"}                   (name->expressions "GNU General Public License v3.0 or later")))
    (is (valid= #{"GPL-3.0-or-later"}                   (name->expressions "GNU General Public License, Version 3 (or later)")))
    (is (valid= #{"GPL-3.0-or-later"}                   (name->expressions "GPL V3+")))
    (is (valid= #{"Hippocratic-2.1"}                    (name->expressions "Hippocratic License")))
    (is (valid= #{"ISC WITH Classpath-exception-2.0"}   (name->expressions "ISC WITH Classpath-exception-2.0")))
    (is (valid= #{"ISC"}                                (name->expressions "ISC Licence")))
    (is (valid= #{"ISC"}                                (name->expressions "ISC License")))
    (is (valid= #{"ISC"}                                (name->expressions "ISC")))
    (is (valid= #{"ISC"}                                (name->expressions "MIT/ISC License")))
    (is (valid= #{"ISC"}                                (name->expressions "MIT/ISC")))
    (is (valid= #{"LGPL-2.1-only"}                      (name->expressions "GNU LESSER GENERAL PUBLIC LICENSE - Version 2.1")))
    (is (valid= #{"LGPL-2.1-only"}                      (name->expressions "GNU LESSER GENERAL PUBLIC LICENSE Version 2.1, February 1999")))
    (is (valid= #{"LGPL-2.1-only"}                      (name->expressions "GNU LGPL v2.1")))
    (is (valid= #{"LGPL-2.1-only"}                      (name->expressions "GNU Lesser General Public License 2.1")))
    (is (valid= #{"LGPL-2.1-only"}                      (name->expressions "GNU Lesser General Public License v2.1")))
    (is (valid= #{"LGPL-2.1-only"}                      (name->expressions "GNU Lesser General Public License, Version 2.1")))
    (is (valid= #{"LGPL-2.1-only"}                      (name->expressions "GNU Lesser General Pulic License v2.1")))
    (is (valid= #{"LGPL-2.1-only"}                      (name->expressions "GNU Library or Lesser General Public License (LGPL) 2.1")))
    (is (valid= #{"LGPL-2.1-only"}                      (name->expressions "GNU Library or Lesser General Public License (LGPL) V2.1")))
    (is (valid= #{"LGPL-2.1-only"}                      (name->expressions "LGPL 2.1")))
    (is (valid= #{"LGPL-2.1-only"}                      (name->expressions "LGPL-2.1")))
    (is (valid= #{"LGPL-2.1-only"}                      (name->expressions "LGPL-2.1-only")))
    (is (valid= #{"LGPL-2.1-only"}                      (name->expressions "LGPLv2.1")))
    (is (valid= #{"LGPL-2.1-only"}                      (name->expressions "lgpl_v2_1")))
    (is (valid= #{"LGPL-2.1-or-later"}                  (name->expressions "GNU Lesser General Public License, version 2.1 or newer")))
    (is (valid= #{"LGPL-3.0-only"}                      (name->expressions "GNU General Lesser Public License (LGPL) version 3.0")))
    (is (valid= #{"LGPL-3.0-only"}                      (name->expressions "GNU LESSER GENERAL PUBLIC LICENSE")))  ; Listed license missing version - we assume the latest
    (is (valid= #{"LGPL-3.0-only"}                      (name->expressions "GNU LESSER GENERAL PUBLIC LICENSE, Version 3.0")))
    (is (valid= #{"LGPL-3.0-only"}                      (name->expressions "GNU LGPL 3")))
    (is (valid= #{"LGPL-3.0-only"}                      (name->expressions "GNU LGPL v3")))
    (is (valid= #{"LGPL-3.0-only"}                      (name->expressions "GNU LGPL version 3")))
    (is (valid= #{"LGPL-3.0-only"}                      (name->expressions "GNU LGPL-3.0")))
    (is (valid= #{"LGPL-3.0-only"}                      (name->expressions "GNU LGPLv3 ")))  ; Note trailing space
    (is (valid= #{"LGPL-3.0-only"}                      (name->expressions "GNU Lesser GPL")))  ; Listed license missing version - we assume the latest
    (is (valid= #{"LGPL-3.0-only"}                      (name->expressions "GNU Lesser General Public Licence 3.0")))
    (is (valid= #{"LGPL-3.0-only"}                      (name->expressions "GNU Lesser General Public Licence")))  ; Listed license missing version - we assume the latest
    (is (valid= #{"LGPL-3.0-only"}                      (name->expressions "GNU Lesser General Public License (LGPL) Version 3")))
    (is (valid= #{"LGPL-3.0-only"}                      (name->expressions "GNU Lesser General Public License (LGPL)")))  ; Listed license missing version - we assume the latest
    (is (valid= #{"LGPL-3.0-only"}                      (name->expressions "GNU Lesser General Public License - v 3")))
    (is (valid= #{"LGPL-3.0-only"}                      (name->expressions "GNU Lesser General Public License - v 3.0")))
    (is (valid= #{"LGPL-3.0-only"}                      (name->expressions "GNU Lesser General Public License - v3")))
    (is (valid= #{"LGPL-3.0-only"}                      (name->expressions "GNU Lesser General Public License v3.0")))
    (is (valid= #{"LGPL-3.0-only"}                      (name->expressions "GNU Lesser General Public License version 3")))
    (is (valid= #{"LGPL-3.0-only"}                      (name->expressions "GNU Lesser General Public License version 3.0")))
    (is (valid= #{"LGPL-3.0-only"}                      (name->expressions "GNU Lesser General Public License")))  ; Listed license missing version - we assume the latest
    (is (valid= #{"LGPL-3.0-only"}                      (name->expressions "GNU Lesser General Public License, Version 3")))
    (is (valid= #{"LGPL-3.0-only"}                      (name->expressions "GNU Lesser Genereal Public License")))  ; Listed license missing version - we assume the latest
    (is (valid= #{"LGPL-3.0-only"}                      (name->expressions "GNU Lesser Public License")))  ; Listed license missing version - we assume the latest
    (is (valid= #{"LGPL-3.0-only"}                      (name->expressions "GNU Library or Lesser General Public License (LGPL)")))  ; Listed license missing version - we assume the latest
    (is (valid= #{"LGPL-3.0-only"}                      (name->expressions "Gnu Lesser Public License")))  ; Listed license missing version - we assume the latest
    (is (valid= #{"LGPL-3.0-only"}                      (name->expressions "L GPL 3")))
    (is (valid= #{"LGPL-3.0-only"}                      (name->expressions "LGPL 3.0 (GNU Lesser General Public License)")))
    (is (valid= #{"LGPL-3.0-only"}                      (name->expressions "LGPL 3.0")))
    (is (valid= #{"LGPL-3.0-only"}                      (name->expressions "LGPL License")))  ; Listed license missing version - we assume the latest
    (is (valid= #{"LGPL-3.0-only"}                      (name->expressions "LGPL Open Source license")))  ; Listed license missing version - we assume the latest
    (is (valid= #{"LGPL-3.0-only"}                      (name->expressions "LGPL v3")))
    (is (valid= #{"LGPL-3.0-only"}                      (name->expressions "LGPL")))  ; Listed license missing version - we assume the latest
    (is (valid= #{"LGPL-3.0-only"}                      (name->expressions "LGPL-3.0")))
    (is (valid= #{"LGPL-3.0-only"}                      (name->expressions "LGPL-3.0-only")))
    (is (valid= #{"LGPL-3.0-only"}                      (name->expressions "LGPLv3")))
    (is (valid= #{"LGPL-3.0-only"}                      (name->expressions "Lesser GPL")))  ; Listed license missing version - we assume the latest
    (is (valid= #{"LGPL-3.0-only"}                      (name->expressions "Lesser General Public License (LGPL)")))  ; Listed license missing version - we assume the latest
    (is (valid= #{"LGPL-3.0-only"}                      (name->expressions "Lesser General Public License")))  ; Listed license missing version - we assume the latest
    (is (valid= #{"LGPL-3.0-or-later"}                  (name->expressions "GNU Lesser General Public License, Version 3 or later")))
    (is (valid= #{"LGPL-3.0-or-later"}                  (name->expressions "GNU Lesser General Public License, v. 3 or later")))
    (is (valid= #{"LGPL-3.0-or-later"}                  (name->expressions "GNU Lesser General Public License, version 3 or later")))
    (is (valid= #{"LGPL-3.0-or-later"}                  (name->expressions "GNU Lesser General Public License, version 3.0 or (at your option) any later version")))
    (is (valid= #{"LGPL-3.0-or-later"}                  (name->expressions "LGPL-3.0-or-later")))
    (is (valid= #{"LGPL-3.0-or-later"}                  (name->expressions "LGPLv3+")))
    (is (valid= #{"LGPL-3.0-or-later"}                  (name->expressions "Licensed under GNU Lesser General Public License Version 3 or later (the ")))  ; Note trailing space
    (is (valid= #{"Libpng"}                             (name->expressions "zlib/libpng License")))
    (is (valid= #{"MIT" "Apache-2.0" "BSD-3-Clause"}    (name->expressions "MIT/Apache-2.0/BSD-3-Clause")))
    (is (valid= #{"MIT"}                                (name->expressions " MIT License")))
    (is (valid= #{"MIT"}                                (name->expressions "Distributed under an MIT-style license (see LICENSE for details).")))
    (is (valid= #{"MIT"}                                (name->expressions "Expat (MIT) license")))
    (is (valid= #{"MIT"}                                (name->expressions "MIT LICENSE")))
    (is (valid= #{"MIT"}                                (name->expressions "MIT Licence")))
    (is (valid= #{"MIT"}                                (name->expressions "MIT Licens")))
    (is (valid= #{"MIT"}                                (name->expressions "MIT License (MIT)")))
    (is (valid= #{"MIT"}                                (name->expressions "MIT License")))
    (is (valid= #{"MIT"}                                (name->expressions "MIT Public License")))
    (is (valid= #{"MIT"}                                (name->expressions "MIT license")))
    (is (valid= #{"MIT"}                                (name->expressions "MIT public License")))
    (is (valid= #{"MIT"}                                (name->expressions "MIT public license")))
    (is (valid= #{"MIT"}                                (name->expressions "MIT")))
    (is (valid= #{"MIT"}                                (name->expressions "MIT-style license (see LICENSE for details).")))
    (is (valid= #{"MIT"}                                (name->expressions "THE MIT LICENSE")))
    (is (valid= #{"MIT"}                                (name->expressions "The MIT Licence")))
    (is (valid= #{"MIT"}                                (name->expressions "The MIT License (MIT) ")))  ; Note trailing space
    (is (valid= #{"MIT"}                                (name->expressions "The MIT License (MIT) | Open Source Initiative")))
    (is (valid= #{"MIT"}                                (name->expressions "The MIT License (MIT)")))
    (is (valid= #{"MIT"}                                (name->expressions "The MIT License")))
    (is (valid= #{"MIT"}                                (name->expressions "The MIT License.")))
    (is (valid= #{"MIT"}                                (name->expressions "http://opensource.org/licenses/MIT")))
;    (is (valid= #{"MIT"}                                (name->expressions "https://github.com/clanhr/clanhr-service/blob/master/LICENSE")))  ; Failing due to https://github.com/spdx/Spdx-Java-Library/issues/182
    (is (valid= #{"MPL-1.0"}                            (name->expressions "Mozilla Public License Version 1.0")))
    (is (valid= #{"MPL-1.1"}                            (name->expressions "Mozilla Public License Version 1.1")))
    (is (valid= #{"MPL-2.0"}                            (name->expressions "MPL 2")))
    (is (valid= #{"MPL-2.0"}                            (name->expressions "MPL 2.0")))
    (is (valid= #{"MPL-2.0"}                            (name->expressions "MPL v2")))
    (is (valid= #{"MPL-2.0"}                            (name->expressions "MPL")))  ; Listed license missing version - we assume the latest
    (is (valid= #{"MPL-2.0"}                            (name->expressions "MPL-2.0")))
    (is (valid= #{"MPL-2.0"}                            (name->expressions "MPL-v2.0")))
    (is (valid= #{"MPL-2.0"}                            (name->expressions "MPL2.0")))
    (is (valid= #{"MPL-2.0"}                            (name->expressions "Mozilla Public Licence 2.0")))
    (is (valid= #{"MPL-2.0"}                            (name->expressions "Mozilla Public License (Version 2.0)")))
    (is (valid= #{"MPL-2.0"}                            (name->expressions "Mozilla Public License 2.0")))
    (is (valid= #{"MPL-2.0"}                            (name->expressions "Mozilla Public License Version 2.0")))
    (is (valid= #{"MPL-2.0"}                            (name->expressions "Mozilla Public License v2.0")))
    (is (valid= #{"MPL-2.0"}                            (name->expressions "Mozilla Public License v2.0+")))
    (is (valid= #{"MPL-2.0"}                            (name->expressions "Mozilla Public License version 2")))
    (is (valid= #{"MPL-2.0"}                            (name->expressions "Mozilla Public License version 2.0")))
    (is (valid= #{"MPL-2.0"}                            (name->expressions "Mozilla Public License")))  ; Listed license missing version - we assume the latest
    (is (valid= #{"MPL-2.0"}                            (name->expressions "Mozilla Public License, v. 2.0")))
    (is (valid= #{"MPL-2.0"}                            (name->expressions "Mozilla Public License, version 2.0")))
    (is (valid= #{"NASA-1.3"}                           (name->expressions "NASA OPEN SOURCE AGREEMENT VERSION 1.3")))
    (is (valid= #{"NASA-1.3"}                           (name->expressions "NASA Open Source Agreement, Version 1.3")))
    (is (valid= #{"NCSA"}                               (name->expressions "University of Illinois/NCSA Open Source License")))
    (is (valid= #{"Ruby"}                               (name->expressions "Ruby License")))
    (is (valid= #{"SGI-B-2.0"}                          (name->expressions "SGI")))  ; Listed license missing version - we assume the latest
    (is (valid= #{"SMPPL"}                              (name->expressions "SMPPL")))
    (is (valid= #{"Unlicense"}                          (name->expressions "The UnLicense")))
    (is (valid= #{"Unlicense"}                          (name->expressions "The Unlicence")))
    (is (valid= #{"Unlicense"}                          (name->expressions "The Unlicense")))
    (is (valid= #{"Unlicense"}                          (name->expressions "UnLicense")))
    (is (valid= #{"Unlicense"}                          (name->expressions "Unlicense License")))
    (is (valid= #{"Unlicense"}                          (name->expressions "Unlicense")))
    (is (valid= #{"Unlicense"}                          (name->expressions "unlicense")))
    (is (valid= #{"W3C"}                                (name->expressions "W3C Software license")))
    (is (valid= #{"WTFPL"}                              (name->expressions "DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE")))
    (is (valid= #{"WTFPL"}                              (name->expressions "DO-WTF-U-WANT-2")))
    (is (valid= #{"WTFPL"}                              (name->expressions "Do What The Fuck You Want To Public License")))
    (is (valid= #{"WTFPL"}                              (name->expressions "Do What The Fuck You Want To Public License, Version 2")))
    (is (valid= #{"WTFPL"}                              (name->expressions "WTFPL v2")))
    (is (valid= #{"WTFPL"}                              (name->expressions "WTFPL – Do What the Fuck You Want to Public License")))
    (is (valid= #{"WTFPL"}                              (name->expressions "WTFPL")))
    (is (valid= #{"X11"}                                (name->expressions "MIT X11 License")))
    (is (valid= #{"X11"}                                (name->expressions "MIT/X11")))
    (is (valid= #{"Zlib"}                               (name->expressions "Zlib License")))
    (is (valid= #{"Zlib"}                               (name->expressions "zlib License")))
    (is (valid= #{"Zlib"}                               (name->expressions "zlib license")))
    (is (valid= #{(lcis/proprietary-commercial)}        (name->expressions "All Rights Reserved")))
    (is (valid= #{(lcis/proprietary-commercial)}        (name->expressions "All rights reserved")))
    (is (valid= #{(lcis/proprietary-commercial)}        (name->expressions "Copyright & all rights reserved Lean Pixel")))
    (is (valid= #{(lcis/proprietary-commercial)}        (name->expressions "Copyright 2013 The Fresh Diet. All rights reserved.")))
    (is (valid= #{(lcis/proprietary-commercial)}        (name->expressions "Copyright 2017 All Rights Reserved")))
    (is (valid= #{(lcis/proprietary-commercial)}        (name->expressions "Not fit for public use so formally proprietary software - this is not open-source")))
    (is (valid= #{(lcis/proprietary-commercial)}        (name->expressions "Private License")))
    (is (valid= #{(lcis/proprietary-commercial)}        (name->expressions "Private")))
    (is (valid= #{(lcis/proprietary-commercial)}        (name->expressions "Proprietary License")))
    (is (valid= #{(lcis/proprietary-commercial)}        (name->expressions "Proprietary")))
    (is (valid= #{(lcis/proprietary-commercial)}        (name->expressions "Proprietory. Copyright Jayaraj Poroor. All Rights Reserved.")))
    (is (valid= #{(lcis/proprietary-commercial)}        (name->expressions "Tulos Commercial License")))
    (is (valid= #{(lcis/proprietary-commercial)}        (name->expressions "Wildbit Proprietary License")))
    (is (valid= #{(lcis/proprietary-commercial)}        (name->expressions "proprietary")))
    (is (valid= #{(lcis/public-domain)}                 (name->expressions "Public Domain")))
    (is (valid= #{(str "GPL-2.0-or-later OR " (lcis/name->unlisted "Swiss Ephemeris"))} (name->expressions "GPL v2+ or Swiss Ephemeris")))
    (is (valid= #{(str "MIT AND " (lcis/proprietary-commercial))} (name->expressions "Dual MIT & Proprietary")))
    (is (unlisted-only?                                 (name->expressions "${license.id}")))
    (is (unlisted-only?                                 (name->expressions "A Clojure library for Google Cloud Pub/Sub.")))
    (is (unlisted-only?                                 (name->expressions "APGL")))  ; Probable typo
    (is (unlisted-only?                                 (name->expressions "Amazon Software License")))
    (is (unlisted-only?                                 (name->expressions "BankersBox License")))
    (is (unlisted-only?                                 (name->expressions "Bespoke")))
    (is (unlisted-only?                                 (name->expressions "Bloomberg Open API")))
    (is (unlisted-only?                                 (name->expressions "Bostock")))
    (is (unlisted-only?                                 (name->expressions "Built In Project License")))
    (is (unlisted-only?                                 (name->expressions "CRAPL License")))
    (is (unlisted-only?                                 (name->expressions "Contact JMonkeyEngine forums for license details")))
    (is (unlisted-only?                                 (name->expressions "Copyright (C) 2015 by Glowbox LLC")))
    (is (unlisted-only?                                 (name->expressions "Copyright (c) 2011 Drew Colthorp")))
    (is (unlisted-only?                                 (name->expressions "Copyright (c) 2017, Lingchao Xin")))
    (is (unlisted-only?                                 (name->expressions "Copyright 2016, klaraHealth, Inc.")))
    (is (unlisted-only?                                 (name->expressions "Copyright 2017 Zensight")))
    (is (unlisted-only?                                 (name->expressions "Copyright 4A Volcano. 2015.")))
    (is (unlisted-only?                                 (name->expressions "Copyright Ona Systems Inc.")))
    (is (unlisted-only?                                 (name->expressions "Copyright meissa GmbH")))
    (is (unlisted-only?                                 (name->expressions "Copyright © SparX 2014")))
    (is (unlisted-only?                                 (name->expressions "Copyright")))
    (is (unlisted-only?                                 (name->expressions "Custom")))
    (is (unlisted-only?                                 (name->expressions "Cydeas Public License")))
    (is (unlisted-only?                                 (name->expressions "Don't steal my stuff")))
    (is (unlisted-only?                                 (name->expressions "Dropbox ToS")))
    (is (unlisted-only?                                 (name->expressions "FIXME: choose")))
    (is (unlisted-only?                                 (name->expressions "Firebase ToS")))
    (is (unlisted-only?                                 (name->expressions "GG Public License")))
    (is (unlisted-only?                                 (name->expressions "Google Maps ToS")))
    (is (unlisted-only?                                 (name->expressions "GraphiQL license")))
    (is (unlisted-only?                                 (name->expressions "Hackthorn Innovation Ltd")))
    (is (unlisted-only?                                 (name->expressions "Hackthorn Innovation copyright")))
    (is (unlisted-only?                                 (name->expressions "Heap ToS")))
    (is (unlisted-only?                                 (name->expressions "Interel")))
    (is (unlisted-only?                                 (name->expressions "JLGL Backend")))
    (is (unlisted-only?                                 (name->expressions "Jedis License")))
    (is (unlisted-only?                                 (name->expressions "Jiegao Owned")))
    (is (unlisted-only?                                 (name->expressions "LICENSE")))
    (is (unlisted-only?                                 (name->expressions "Libre Uso MX")))
    (is (unlisted-only?                                 (name->expressions "License of respective package")))
    (is (unlisted-only?                                 (name->expressions "License")))
    (is (unlisted-only?                                 (name->expressions "Like Clojure.")))
    (is (unlisted-only?                                 (name->expressions "Mixed")))
    (is (unlisted-only?                                 (name->expressions "Multiple")))
    (is (unlisted-only?                                 (name->expressions "OTN License Agreement")))
    (is (unlisted-only?                                 (name->expressions "Open Source Community License - Type C version 1.0")))
    (is (unlisted-only?                                 (name->expressions "Other License")))
    (is (unlisted-only?                                 (name->expressions "Provisdom")))
    (is (unlisted-only?                                 (name->expressions "Research License 1.0")))
    (is (unlisted-only?                                 (name->expressions "Restricted Distribution.")))
    (is (unlisted-only?                                 (name->expressions "SYNNEX China Owned")))
    (is (unlisted-only?                                 (name->expressions "See the LICENSE file")))
    (is (unlisted-only?                                 (name->expressions "Shen License")))
    (is (unlisted-only?                                 (name->expressions "Slick2D License")))
    (is (unlisted-only?                                 (name->expressions "Stripe ToS")))
    (is (unlisted-only?                                 (name->expressions "TODO")))
    (is (unlisted-only?                                 (name->expressions "TODO: Choose a license")))
    (is (unlisted-only?                                 (name->expressions "The I Haven't Got Around To This Yet License")))
    (is (unlisted-only?                                 (name->expressions "To ill!")))
    (is (unlisted-only?                                 (name->expressions "UNLICENSED")))
    (is (unlisted-only?                                 (name->expressions "University of Buffalo Public License")))
    (is (unlisted-only?                                 (name->expressions "Unknown")))
    (is (unlisted-only?                                 (name->expressions "VNETLPL - Limited Public License")))
    (is (unlisted-only?                                 (name->expressions "VNet PL")))
    (is (unlisted-only?                                 (name->expressions "Various")))
    (is (unlisted-only?                                 (name->expressions "Vimeo License")))
    (is (unlisted-only?                                 (name->expressions "WIP")))
    (is (unlisted-only?                                 (name->expressions "YouTube ToS")))
    (is (unlisted-only?                                 (name->expressions "avi license")))
    (is (unlisted-only?                                 (name->expressions "esl-sdk-external-signer-verification")))
    (is (unlisted-only?                                 (name->expressions "https://github.com/jaycfields/jry/blob/master/README.md#license")))  ; We don't support full text matching in Markdown yet
    (is (unlisted-only?                                 (name->expressions "jank license")))
    (is (unlisted-only?                                 (name->expressions "name")))
    (is (unlisted-only?                                 (name->expressions "none")))
    (is (unlisted-only?                                 (name->expressions "state-node license")))
    (is (unlisted-only?                                 (name->expressions "trove")))
    (is (unlisted-only?                                 (name->expressions "url")))
    (is (unlisted-only?                                 (name->expressions "wisdragon")))
    (is (unlisted-only?                                 (name->expressions "wiseloong")))))

(deftest name->expressions-info-tests
  (testing "Nil, empty or blank"
    (is (nil?                                           (name->expressions-info nil)))
    (is (nil?                                           (name->expressions-info "")))
    (is (nil?                                           (name->expressions-info "       ")))
    (is (nil?                                           (name->expressions-info "\n")))
    (is (nil?                                           (name->expressions-info "\t"))))
  (testing "SPDX license ids"
    (is (valid-info= {"AGPL-3.0-only" (list {:type :declared :strategy :spdx-expression :source (list "AGPL-3.0")})}
                     (name->expressions-info "AGPL-3.0")))
    (is (valid-info= {"GPL-2.0-only WITH Classpath-exception-2.0" (list {:type :declared :strategy :spdx-expression :source (list "GPL-2.0-with-classpath-exception")})}
                     (name->expressions-info "GPL-2.0-with-classpath-exception"))))
  (testing "SPDX expressions"
    (is (valid-info= {"GPL-2.0-only WITH Classpath-exception-2.0" (list {:type :declared :strategy :spdx-expression :source (list "GPL-2.0 WITH Classpath-exception-2.0")})}
               (name->expressions-info "GPL-2.0 WITH Classpath-exception-2.0"))))
  (testing "Single expressions that are not valid SPDX"
    (is (valid-info= {"GPL-2.0-only WITH Classpath-exception-2.0" (list {:type :concluded :confidence :low :strategy :expression-inference}
                                                                        {:id "GPL-2.0-only" :type :concluded :confidence :low :strategy :regex-matching :source (list "GNU General Public License, version 2")}
                                                                        {:id "Classpath-exception-2.0" :type :concluded :confidence :low :strategy :regex-matching :source (list "Classpath Exception")})}
                     (name->expressions-info "GNU General Public License, version 2 with the GNU Classpath Exception"))))
  (testing "Multiple expressions"
    (is (valid-info= {"MIT"          (list {:id "MIT"          :type :concluded :confidence :high :strategy :regex-matching :source (list "MIT")})
                      "BSD-4-Clause" (list {:id "BSD-4-Clause" :type :concluded :confidence :low  :strategy :regex-matching :source (list "BSD")})}
                     (name->expressions-info "MIT / BSD"))))
  (testing "Some names from Clojars"
    (is (valid-info= {"BSD-3-Clause" (list {:id "BSD-3-Clause" :type :concluded :confidence :medium :strategy :spdx-listed-uri :source (list "https://opensource.org/licenses/BSD-3-Clause")})}
                     (name->expressions-info "https://opensource.org/licenses/BSD-3-Clause")))
    (is (valid-info= {"EPL-2.0" (list {:id "EPL-2.0" :type :concluded :confidence :medium :strategy :regex-matching :source (list "Eclipse Public License - v 2.0")})}
                     (name->expressions-info "Eclipse Public License - v 2.0")))))

(deftest uri->ids-tests
  (testing "Nil, empty or blank uri"
    (is (nil?                           (uri->ids nil)))
    (is (nil?                           (uri->ids "")))
    (is (nil?                           (uri->ids "       ")))
    (is (nil?                           (uri->ids "\n")))
    (is (nil?                           (uri->ids "\t"))))
  (testing "URIs that appear verbatim in the SPDX license or exception lists"
    (is (= #{"Apache-2.0"}              (uri->ids "http://www.apache.org/licenses/LICENSE-2.0.html")))
    (is (= #{"Apache-2.0"}              (uri->ids "               http://www.apache.org/licenses/LICENSE-2.0.html             ")))   ; Test whitespace
    (is (= #{"AGPL-3.0-or-later"}       (uri->ids "https://www.gnu.org/licenses/agpl.txt")))
    (is (= #{"CC-BY-SA-4.0"}            (uri->ids "https://creativecommons.org/licenses/by-sa/4.0/legalcode")))
    (is (= #{"Classpath-exception-2.0"} (uri->ids "https://www.gnu.org/software/classpath/license.html"))))
  (testing "URI variations that should be handled identically"
    (is (= #{"Apache-2.0"}              (uri->ids "https://www.apache.org/licenses/LICENSE-2.0.html")))
    (is (= #{"Apache-2.0"}              (uri->ids "http://www.apache.org/licenses/LICENSE-2.0.html")))
    (is (= #{"Apache-2.0"}              (uri->ids "https://www.apache.org/licenses/LICENSE-2.0.txt")))
    (is (= #{"Apache-2.0"}              (uri->ids "http://apache.org/licenses/LICENSE-2.0.pdf"))))
  (testing "URIs that appear in licensey things, but aren't in the SPDX license list as shown"
    (is (= #{"Apache-2.0"}              (uri->ids "http://www.apache.org/licenses/LICENSE-2.0")))
    (is (= #{"Apache-2.0"}              (uri->ids "https://www.apache.org/licenses/LICENSE-2.0.txt"))))
  (testing "URIs that aren't in the SPDX license list, but do match via retrieval and full text matching"
    (is (= #{"Apache-2.0"}              (uri->ids "https://raw.githubusercontent.com/pmonks/lice-comb/main/LICENSE")))
    (is (= #{"Apache-2.0"}              (uri->ids "https://github.com/pmonks/lice-comb/blob/main/LICENSE")))
    (is (= #{"Apache-2.0"}              (uri->ids "HTTPS://GITHUB.COM/pmonks/lice-comb/blob/main/LICENSE")))))
