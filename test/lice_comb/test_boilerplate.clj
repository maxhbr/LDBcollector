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
(def ^:private global-setup (delay
                              ; Because java.util.logging is a hot mess
                              (org.slf4j.bridge.SLF4JBridgeHandler/removeHandlersForRootLogger)
                              (org.slf4j.bridge.SLF4JBridgeHandler/install)

                              ; Enable spec validation
                              (spec/check-asserts true)

                              (println "\n☔️ Running tests on Clojure" (clojure-version) "/ JVM" (System/getProperty "java.version") (str "(" (System/getProperty "java.vm.name") " v" (System/getProperty "java.vm.version") ")\n"))
                              nil))

(defn fixture
  [f]
  @global-setup
  (f))

(def not-nil? (complement nil?))

(defn when-pred
  [val pred then]
  (if (pred val)
    (then val)
    val))

(defmacro testing-with-data
  "A form of `clojure.test/testing` that generates multiple `clojure.test/is`
  clauses, based on applying f to the keys in m, and comparing to the associated
  value in m."
  [name f m]
  `(clojure.test/testing ~name
     ~@(map #(list `clojure.test/is `(= (~f ~(key %)) ~(when-pred (val %) list? (partial list 'quote))))
            (if (isa? (type m) clojure.lang.Symbol)
              @(resolve m)
              m))))

(defn valid=
  "Returns true if all of the following are true:
  * s2 has metadata
  * s2 is a set
  * s2 is equal to s1
  * every entry in s2 is a valid SPDX license expression

  Also prints (to stdout) which of the above is not true, in the event that any
  of them are not true."
  [s1 s2]
  (let [metadata?              (or (nil? s2) (not-nil? (meta s2)))
        is-a-set?              (or (nil? s2) (set? s2))
        is-equal?              (= s1 s2)
        all-valid-expressions? (and (set? s2) (every? true? (map sexp/valid? s2)))
        result                 (and metadata?
                                    is-a-set?
                                    is-equal?
                                    all-valid-expressions?)]
    ; Yes print here is deliberate, to ensure the output lines are grouped with the associated test failure message
    (when-not result                 (print "\n☔️☔️☔️ Invalid result produced:"))
    (when-not metadata?              (print "\n* Missing metadata"))
    (when-not is-a-set?              (print "\n* Not a set"))
    (when-not is-equal?              (print "\n* Not equal to expected value"))
    (when-not all-valid-expressions? (print "\n* Not all valid SPDX expressions"))
    result))
