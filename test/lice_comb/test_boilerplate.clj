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

(ns lice-comb.test-boilerplate
  (:require [clojure.spec.alpha :as spec]
            [spdx.expressions   :as sexp]))

; Here we hack up a "global once" function
(def ^:private global-setup (memoize (fn []
                                       ; Because java.util.logging is a hot mess
                                       (org.slf4j.bridge.SLF4JBridgeHandler/removeHandlersForRootLogger)
                                       (org.slf4j.bridge.SLF4JBridgeHandler/install)

                                       ; Enable spec validation
                                       (spec/check-asserts true)

                                       (println "\n☔️ Running tests on Clojure" (clojure-version) "/ JVM" (System/getProperty "java.version") (str "(" (System/getProperty "java.vm.name") " v" (System/getProperty "java.vm.version") ")\n"))
                                       )))

(defn fixture
  [f]
  (global-setup)
  (f))

(def not-nil? (complement nil?))

(defn valid=
  "Returns true if all of the SPDX exceptions in s2 are valid, and also
  that s1 equals s2."
  [s1 s2]
  (let [metadata?              (not-nil? (meta s2))
        is-a-set?              (set?     s2)
        is-equal?              (= s1 s2)
        all-valid-expressions? (every? true? (map sexp/valid? s2))]
    (when-not metadata?              (println "☔️ Missing metadata"))
    (when-not is-a-set?              (println "☔️ Not a set"))
    (when-not is-equal?              (println "☔️ Not equal to expected value"))
    (when-not all-valid-expressions? (println "☔️ Not all valid SPDX expressions"))
    (and metadata?
         is-a-set?
         is-equal?
         all-valid-expressions?)))

