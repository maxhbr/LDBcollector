;
; Copyright © 2023 Peter Monks
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

(ns lice-comb.impl.matching-test
  (:require [clojure.test               :refer [deftest testing is use-fixtures]]
            [lice-comb.test-boilerplate :refer [fixture]]
            [lice-comb.impl.matching    :refer [split-on-operators]]))

(use-fixtures :once fixture)

(deftest split-on-operators-tests
  (testing "nil/empty/blank"
    (is (nil? (split-on-operators nil)))
    (is (nil? (split-on-operators "")))
    (is (nil? (split-on-operators "  "))))
  (testing "Simple non-splits"
    (is (= '("foo")            (split-on-operators "foo")))
    (is (= '("Apache")         (split-on-operators "Apache")))
    (is (= '("Apache MIT BSD") (split-on-operators "Apache MIT BSD")))
    (is (= '("ApacheandMIT")   (split-on-operators "ApacheandMIT")))
    (is (= '("Apacheand MIT")  (split-on-operators "Apacheand MIT")))
    (is (= '("Apache andMIT")  (split-on-operators "Apache andMIT")))
    (is (= '("ApacheorMIT")    (split-on-operators "ApacheorMIT")))
    (is (= '("Apacheor MIT")   (split-on-operators "Apacheor MIT")))
    (is (= '("Apache orMIT")   (split-on-operators "Apache orMIT")))
    (is (= '("ApachewithMIT")  (split-on-operators "ApachewithMIT")))
    (is (= '("Apachewith MIT") (split-on-operators "Apachewith MIT")))
    (is (= '("Apache withMIT") (split-on-operators "Apache withMIT")))
    (is (= '("Apachew/MIT")    (split-on-operators "Apachew/MIT")))
    (is (= '("Apachew/ MIT")   (split-on-operators "Apachew/ MIT"))))
  (testing "Simple and splits"
    (is (= '("Apache" :and "MIT") (split-on-operators "Apache and MIT")))
    (is (= '("Apache" :and "MIT") (split-on-operators "Apache AND MIT")))
    (is (= '("Apache" :and "MIT") (split-on-operators "Apache aNd MIT")))
    (is (= '("Apache" :and "MIT") (split-on-operators "Apache & MIT")))
    (is (= '("Apache" :and "MIT") (split-on-operators "Apache &MIT")))
    (is (= '("Apache" :and "MIT") (split-on-operators "Apache&MIT"))))
  (testing "Simple or splits"
    (is (= '("Apache" :or "MIT") (split-on-operators "Apache or MIT")))
    (is (= '("Apache" :or "MIT") (split-on-operators "Apache OR MIT")))
    (is (= '("Apache" :or "MIT") (split-on-operators "Apache oR MIT"))))
  (testing "Simple with splits"
    (is (= '("Apache" :with "MIT") (split-on-operators "Apache with MIT")))
    (is (= '("Apache" :with "MIT") (split-on-operators "Apache WITH MIT")))
    (is (= '("Apache" :with "MIT") (split-on-operators "Apache wItH MIT")))
    (is (= '("Apache" :with "MIT") (split-on-operators "Apache w/ MIT")))
    (is (= '("Apache" :with "MIT") (split-on-operators "Apache w/MIT"))))
  (testing "Complex non-splits"
    (is (= '("COMMON DEVELOPMENT AND DISTRIBUTION LICENSE Version 1.0") (split-on-operators "COMMON DEVELOPMENT AND DISTRIBUTION LICENSE Version 1.0")))
    (is (= '("Copyright & all rights reserved Lean Pixel")              (split-on-operators "Copyright & all rights reserved Lean Pixel")))
    (is (= '("GNU General Public License v3.0 or later")                (split-on-operators "GNU General Public License v3.0 or later")))
    (is (= '("GNU General Public License, Version 3 (or later)")        (split-on-operators "GNU General Public License, Version 3 (or later)")))
    (is (= '("GNU Lesser General Public License, version 2.1 or newer") (split-on-operators "GNU Lesser General Public License, version 2.1 or newer")))
    (is (= '("LGPL-3.0-or-later")                                       (split-on-operators "LGPL-3.0-or-later")))))
