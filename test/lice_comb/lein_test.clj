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

(ns lice-comb.lein-test
  (:require [clojure.test               :refer [deftest testing is use-fixtures]]
            [lice-comb.test-boilerplate :refer [fixture valid=]]
            [lice-comb.impl.spdx        :as lcis]
            [lice-comb.lein             :refer [dep->expressions deps->expressions]]))

(use-fixtures :once fixture)

; We keep these short, as this is basically just a thin wrapper around lice-comb.deps
(deftest dep->ids-tests
  (testing "Nil deps"
    (is (nil? (dep->expressions nil))))
  (testing "Invalid deps"
    (is (nil? (dep->expressions ['com.github.pmonks/invalid-project "0.0.1"])))  ; Invalid GA
    (is (nil? (dep->expressions ['org.clojure/clojure "1.0.0-SNAPSHOT"]))))      ; Invalid V
  (testing "Valid deps - single license"
    (is (= #{"Apache-2.0"}         (dep->expressions ['com.github.pmonks/asf-cat "1.0.12"])))
    (is (= #{"EPL-1.0"}            (dep->expressions ['org.clojure/clojure "1.10.3"])))
    (is (= #{"BSD-4-Clause"}       (dep->expressions ['org.ow2.asm/asm "5.2"])))
    (is (= #{(lcis/public-domain)} (dep->expressions ['aopalliance/aopalliance "1.0"])))
    (is (= #{"CDDL-1.0"}           (dep->expressions ['javax.activation/activation "1.1.1"])))
    (is (= #{"CC0-1.0"}            (dep->expressions ['net.i2p.crypto/eddsa "0.3.0"])))
    (is (= #{"GPL-3.0-only"}       (dep->expressions ['org.activecomponents.jadex/jadex-distribution-minimal "4.0.250"])))
    (is (= #{"Apache-2.0"}         (dep->expressions ['software.amazon.ion/ion-java "1.0.0"]))))
  (testing "Valid deps - no licenses in deployed artifacts -> leverage fallbacks"
    (is (nil?                      (dep->expressions ['slipset/deps-deploy         "0.2.0"])))
    (is (nil?                      (dep->expressions ['borkdude/sci.impl.reflector "0.0.1"]))))
  (testing "Valid deps - multi license"
    (is (= #{"EPL-1.0" "LGPL-3.0-only"} (dep->expressions ['ch.qos.logback/logback-classic "1.2.7"])))  ; Note: <url> implies LGPL-2.1-only, but name is ambiguous
    (is (= #{"CDDL-1.1" "GPL-2.0-only WITH Classpath-exception-2.0"}
           (dep->expressions ['javax.mail/mail "1.4.7"]))))
  (testing "Valid deps - Maven classifiers"
;    (is (= #{"Apache-2.0" "LGPL-3.0-or-later"} (dep->expressions ['com.github.jnr/jffi$native "1.3.11}])))))    ; Blocked on https://github.com/jnr/jffi/issues/141
    (is (= #{"Apache-2.0"}         (dep->expressions ['com.github.jnr/jffi$native "1.3.11"])))))

; Note: we can't use valid= or valid-info= here, since the results from deps->expressions are unique
(deftest deps-expressions-test
  (testing "Nil and empty deps"
    (is (nil? (deps->expressions nil)))
    (is (= {} (deps->expressions []))))
  (testing "Single deps"
    (is (= {['org.clojure/clojure "1.10.3"] #{"EPL-1.0"}}
           (deps->expressions [['org.clojure/clojure "1.10.3"]]))))
  (testing "Multiple deps"
    (is (= {'[org.clojure/clojure                     "1.10.3"]  #{"EPL-1.0"}
            '[org.clojure/spec.alpha                  "0.2.194"] #{"EPL-1.0"}
            '[cheshire/cheshire                       "5.10.1"]  #{"MIT"}
            '[com.fasterxml.jackson.core/jackson-core "2.12.4"]  #{"Apache-2.0"}}
           (deps->expressions [['org.clojure/clojure                     "1.10.3"]
                               ['org.clojure/spec.alpha                  "0.2.194"]
                               ['cheshire/cheshire                       "5.10.1"]
                               ['com.fasterxml.jackson.core/jackson-core "2.12.4"]])))))
