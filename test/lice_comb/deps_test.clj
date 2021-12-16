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

(ns lice-comb.deps-test
  (:require [clojure.test    :refer [deftest testing is]]
            [lice-comb.deps  :refer [dep->ids deps-licenses]]))

(def gitlib-dir (str (System/getProperty "user.home") "/.gitlibs/libs"))

(deftest dep->ids-tests
  (testing "Nil deps"
    (is (nil? (dep->ids nil))))
  (testing "Valid deps - single license"
    (is (= #{"Apache-2.0"}             (dep->ids ['com.github.pmonks/asf-cat  {:deps/manifest :mvn :mvn/version "1.0.12"}])))
    (is (= #{"EPL-1.0"}                (dep->ids ['org.clojure/clojure        {:deps/manifest :mvn :mvn/version "1.10.3"}])))
    (is (= #{"EPL-1.0"}                (dep->ids ['com.github.athos/clj-check {:deps/manifest :deps :deps/root (str gitlib-dir "/com.github.athos/clj-check") :lice-comb/licenses #{"EPL-1.0"}}])))
    (is (= #{"BSD-3-Clause"}           (dep->ids ['org.ow2.asm/asm            {:deps/manifest :mvn :mvn/version "5.2"}])))
    (is (= #{"NON-SPDX-Public-Domain"} (dep->ids ['aopalliance/aopalliance    {:deps/manifest :mvn :mvn/version "1.0"}]))))
  (testing "Valid deps - no licenses in deployed artifacts -> leverage fallbacks"
    (is (= #{"EPL-1.0"} (dep->ids ['slipset/deps-deploy         {:deps/manifest :mvn :mvn/version "0.2.0"}])))
    (is (= #{"EPL-1.0"} (dep->ids ['borkdude/sci.impl.reflector {:deps/manifest :mvn :mvn/version "0.0.1"}]))))
  (testing "Valid deps - multi license"
    (is (= #{"GPL-2.0-with-classpath-exception" "MIT"} (dep->ids ['org.checkerframework/checker-compat-qual {:deps/manifest :mvn :mvn/version "2.5.5"}])))))

(deftest deps-licenses-test
  (testing "Nil and empty deps"
    (is (nil? (deps-licenses nil)))
    (is (= {} (deps-licenses {}))))
  (testing "Single deps"
    (is (= {'org.clojure/clojure {:deps/manifest :mvn :mvn/version "1.10.3" :lice-comb/licenses #{"EPL-1.0"}}}
           (deps-licenses {'org.clojure/clojure {:deps/manifest :mvn :mvn/version "1.10.3"}})))
    (is (= {'com.github.athos/clj-check {:deps/manifest :deps :deps/root (str gitlib-dir "/com.github.athos/clj-check") :lice-comb/licenses #{"EPL-1.0"}}}   ; Note: we use this, as we use it so we can be sure it's been downloaded before this test is run
           (deps-licenses {'com.github.athos/clj-check {:deps/manifest :deps :deps/root (str gitlib-dir "/com.github.athos/clj-check")}}))))
  (testing "Multiple deps"
    (is (= {'org.clojure/clojure                                       {:deps/manifest :mvn :mvn/version "1.10.3" :lice-comb/licenses #{"EPL-1.0"}}
            'org.clojure/spec.alpha                                    {:deps/manifest :mvn :mvn/version "0.2.194" :lice-comb/licenses #{"EPL-1.0"}}
            'org.clojure/core.specs.alpha                              {:deps/manifest :mvn :mvn/version "0.2.56" :lice-comb/licenses #{"EPL-1.0"}}
            'org.clojure/data.xml                                      {:deps/manifest :mvn :mvn/version "0.2.0-alpha6" :lice-comb/licenses #{"EPL-1.0"}}
            'org.clojure/data.codec                                    {:deps/manifest :mvn :mvn/version "0.1.0" :lice-comb/licenses #{"EPL-1.0"}}
            'cheshire/cheshire                                         {:deps/manifest :mvn :mvn/version "5.10.1" :lice-comb/licenses #{"MIT"}}
            'com.fasterxml.jackson.core/jackson-core                   {:deps/manifest :mvn :mvn/version "2.12.4" :lice-comb/licenses #{"Apache-2.0"}}
            'com.fasterxml.jackson.dataformat/jackson-dataformat-smile {:deps/manifest :mvn :mvn/version "2.12.4" :lice-comb/licenses #{"Apache-2.0"}}
            'com.fasterxml.jackson.core/jackson-databind               {:deps/manifest :mvn :mvn/version "2.12.4" :lice-comb/licenses #{"Apache-2.0"}}
            'com.fasterxml.jackson.core/jackson-annotations            {:deps/manifest :mvn :mvn/version "2.12.4" :lice-comb/licenses #{"Apache-2.0"}}
            'com.fasterxml.jackson.dataformat/jackson-dataformat-cbor  {:deps/manifest :mvn :mvn/version "2.12.4" :lice-comb/licenses #{"Apache-2.0"}}
            'tigris/tigris                                             {:deps/manifest :mvn :mvn/version "0.1.2" :lice-comb/licenses #{"EPL-1.0"}}
            'clj-xml-validation/clj-xml-validation                     {:deps/manifest :mvn :mvn/version "1.0.2" :lice-comb/licenses #{"EPL-1.0"}}
            'camel-snake-kebab/camel-snake-kebab                       {:deps/manifest :mvn :mvn/version "0.4.2" :lice-comb/licenses #{"EPL-1.0"}}
            'tolitius/xml-in                                           {:deps/manifest :mvn :mvn/version "0.1.1" :lice-comb/licenses #{"EPL-1.0"}}}
           (deps-licenses {'org.clojure/clojure                                       {:deps/manifest :mvn :mvn/version "1.10.3"}
                           'org.clojure/spec.alpha                                    {:deps/manifest :mvn :mvn/version "0.2.194"}
                           'org.clojure/core.specs.alpha                              {:deps/manifest :mvn :mvn/version "0.2.56"}
                           'org.clojure/data.xml                                      {:deps/manifest :mvn :mvn/version "0.2.0-alpha6"}
                           'org.clojure/data.codec                                    {:deps/manifest :mvn :mvn/version "0.1.0"}
                           'cheshire/cheshire                                         {:deps/manifest :mvn :mvn/version "5.10.1"}
                           'com.fasterxml.jackson.core/jackson-core                   {:deps/manifest :mvn :mvn/version "2.12.4"}
                           'com.fasterxml.jackson.dataformat/jackson-dataformat-smile {:deps/manifest :mvn :mvn/version "2.12.4"}
                           'com.fasterxml.jackson.core/jackson-databind               {:deps/manifest :mvn :mvn/version "2.12.4"}
                           'com.fasterxml.jackson.core/jackson-annotations            {:deps/manifest :mvn :mvn/version "2.12.4"}
                           'com.fasterxml.jackson.dataformat/jackson-dataformat-cbor  {:deps/manifest :mvn :mvn/version "2.12.4"}
                           'tigris/tigris                                             {:deps/manifest :mvn :mvn/version "0.1.2"}
                           'clj-xml-validation/clj-xml-validation                     {:deps/manifest :mvn :mvn/version "1.0.2"}
                           'camel-snake-kebab/camel-snake-kebab                       {:deps/manifest :mvn :mvn/version "0.4.2"}
                           'tolitius/xml-in                                           {:deps/manifest :mvn :mvn/version "0.1.1"}})))
    (is (= {'org.clojure/clojure                   {:deps/manifest :mvn :mvn/version "1.10.3" :lice-comb/licenses #{"EPL-1.0"}}
            'org.clojure/spec.alpha                {:deps/manifest :mvn :mvn/version "0.2.194" :lice-comb/licenses #{"EPL-1.0"}}
            'org.clojure/core.specs.alpha          {:deps/manifest :mvn :mvn/version "0.2.56" :lice-comb/licenses #{"EPL-1.0"}}
            'org.clojure/data.xml                  {:deps/manifest :mvn :mvn/version "0.2.0-alpha6" :lice-comb/licenses #{"EPL-1.0"}}
            'org.clojure/data.codec                {:deps/manifest :mvn :mvn/version "0.1.0" :lice-comb/licenses #{"EPL-1.0"}}
            'tigris/tigris                         {:deps/manifest :mvn :mvn/version "0.1.2" :lice-comb/licenses #{"EPL-1.0"}}
            'clj-xml-validation/clj-xml-validation {:deps/manifest :mvn :mvn/version "1.0.2" :lice-comb/licenses #{"EPL-1.0"}}
            'camel-snake-kebab/camel-snake-kebab   {:deps/manifest :mvn :mvn/version "0.4.2" :lice-comb/licenses #{"EPL-1.0"}}
            'tolitius/xml-in                       {:deps/manifest :mvn :mvn/version "0.1.1" :lice-comb/licenses #{"EPL-1.0"}}
            'com.github.athos/clj-check            {:deps/manifest :deps :deps/root (str gitlib-dir "/com.github.athos/clj-check") :lice-comb/licenses #{"EPL-1.0"}}}
           (deps-licenses {'org.clojure/clojure                   {:deps/manifest :mvn :mvn/version "1.10.3"}
                           'org.clojure/spec.alpha                {:deps/manifest :mvn :mvn/version "0.2.194"}
                           'org.clojure/core.specs.alpha          {:deps/manifest :mvn :mvn/version "0.2.56"}
                           'org.clojure/data.xml                  {:deps/manifest :mvn :mvn/version "0.2.0-alpha6"}
                           'org.clojure/data.codec                {:deps/manifest :mvn :mvn/version "0.1.0"}
                           'tigris/tigris                         {:deps/manifest :mvn :mvn/version "0.1.2"}
                           'clj-xml-validation/clj-xml-validation {:deps/manifest :mvn :mvn/version "1.0.2"}
                           'camel-snake-kebab/camel-snake-kebab   {:deps/manifest :mvn :mvn/version "0.4.2"}
                           'tolitius/xml-in                       {:deps/manifest :mvn :mvn/version "0.1.1"}
                           'com.github.athos/clj-check            {:deps/manifest :deps :deps/root (str gitlib-dir "/com.github.athos/clj-check")}})))))
