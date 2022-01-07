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
  (:require [clojure.spec.alpha :as spec]))

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
