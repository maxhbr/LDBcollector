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
  (:require [clojure.test               :refer [deftest testing is use-fixtures]]
            [lice-comb.test-boilerplate :refer [fixture valid=]]
            [lice-comb.impl.spdx        :as lcis]
            [lice-comb.deps             :refer [dep->expressions deps-expressions]]))

(use-fixtures :once fixture)

(def gitlib-dir (str (System/getProperty "user.home") "/.gitlibs/libs"))

(deftest dep->expressions-tests
  (testing "Nil deps"
    (is (nil? (dep->expressions nil))))
  (testing "Unknown dep types"
    (is (thrown? clojure.lang.ExceptionInfo (dep->expressions ['com.github.pmonks/lice-comb {:deps/manifest :invalid :mvn/version "1.0.0"}]))))
  (testing "Invalid deps"
    (is (nil? (dep->expressions ['com.github.pmonks/invalid-project             {:deps/manifest :mvn :mvn/version "0.0.1"}])))                  ; Invalid GA
    (is (nil? (dep->expressions ['org.clojure/clojure                           {:deps/manifest :mvn :mvn/version "1.0.0-SNAPSHOT"}])))         ; Invalid V
    (is (nil? (dep->expressions ['org.codehaus.plexus/plexus-container-default  {:deps/manifest :mvn :mvn/version "1.0-alpha-9-stable-1"}]))))  ; Malformed parent POM
  (testing "Valid deps - single license"
    (is (valid= #{"Apache-2.0"}         (dep->expressions ['com.github.pmonks/asf-cat                                 {:deps/manifest :mvn :mvn/version "1.0.12"}])))
    (is (valid= #{"EPL-1.0"}            (dep->expressions ['org.clojure/clojure                                       {:deps/manifest :mvn :mvn/version "1.10.3"}])))
    (is (valid= #{"EPL-1.0"}            (dep->expressions ['com.github.athos/clj-check                                {:deps/manifest :deps :git/sha "518d5a1cbfcd7c952f548e6dbfcb9a4a5faf9062" :deps/root (str gitlib-dir "/com.github.athos/clj-check")}])))    ; Note: we use this git dep, as it's used earlier in the build, so we can be sure it's been downloaded before this test is run
    (is (valid= #{"BSD-4-Clause"}       (dep->expressions ['org.ow2.asm/asm                                           {:deps/manifest :mvn :mvn/version "5.2"}])))
    (is (valid= #{(lcis/public-domain)} (dep->expressions ['aopalliance/aopalliance                                   {:deps/manifest :mvn :mvn/version "1.0"}])))
    (is (valid= #{"Apache-2.0"}         (dep->expressions ['com.amazonaws/aws-java-sdk-core                           {:deps/manifest :mvn :mvn/version "1.12.129"}])))
    (is (valid= #{"Apache-2.0"}         (dep->expressions ['com.amazonaws/aws-java-sdk-kms                            {:deps/manifest :mvn :mvn/version "1.12.129"}])))
    (is (valid= #{"Apache-2.0"}         (dep->expressions ['com.amazonaws/aws-java-sdk-s3                             {:deps/manifest :mvn :mvn/version "1.12.129"}])))
    (is (valid= #{"Apache-2.0"}         (dep->expressions ['com.amazonaws/aws-java-sdk-sts                            {:deps/manifest :mvn :mvn/version "1.12.129"}])))
    (is (valid= #{"Apache-2.0"}         (dep->expressions ['com.fasterxml.jackson.dataformat/jackson-dataformat-cbor  {:deps/manifest :mvn :mvn/version "2.13.0"}])))
    (is (valid= #{"Apache-2.0"}         (dep->expressions ['com.fasterxml.jackson.dataformat/jackson-dataformat-smile {:deps/manifest :mvn :mvn/version "2.13.0"}])))
    (is (valid= #{"Apache-2.0"}         (dep->expressions ['com.google.guava/guava                                    {:deps/manifest :mvn :mvn/version "31.0.1-jre"}])))
    (is (valid= #{"Apache-2.0"}         (dep->expressions ['io.opentracing/opentracing-api                            {:deps/manifest :mvn :mvn/version "0.33.0"}])))
    (is (valid= #{"Apache-2.0"}         (dep->expressions ['io.opentracing/opentracing-mock                           {:deps/manifest :mvn :mvn/version "0.33.0"}])))
    (is (valid= #{"Apache-2.0"}         (dep->expressions ['io.opentracing/opentracing-noop                           {:deps/manifest :mvn :mvn/version "0.33.0"}])))
    (is (valid= #{"Apache-2.0"}         (dep->expressions ['io.opentracing/opentracing-util                           {:deps/manifest :mvn :mvn/version "0.33.0"}])))
    (is (valid= #{"CDDL-1.0"}           (dep->expressions ['javax.activation/activation                               {:deps/manifest :mvn :mvn/version "1.1.1"}])))
    (is (valid= #{"CDDL-1.0"}           (dep->expressions ['javax.annotation/jsr250-api                               {:deps/manifest :mvn :mvn/version "1.0"}])))
    (is (valid= #{"Apache-2.0"}         (dep->expressions ['javax.enterprise/cdi-api                                  {:deps/manifest :mvn :mvn/version "2.0"}])))
    (is (valid= #{"Apache-2.0"}         (dep->expressions ['javax.inject/javax.inject                                 {:deps/manifest :mvn :mvn/version "1"}])))
    (is (valid= #{"EPL-1.0"}            (dep->expressions ['junit/junit                                               {:deps/manifest :mvn :mvn/version "4.13.2"}])))
    (is (valid= #{"CC0-1.0"}            (dep->expressions ['net.i2p.crypto/eddsa                                      {:deps/manifest :mvn :mvn/version "0.3.0"}])))
    (is (valid= #{"Apache-2.0"}         (dep->expressions ['net.jpountz.lz4/lz4                                       {:deps/manifest :mvn :mvn/version "1.3.0"}])))
    (is (valid= #{"GPL-3.0-only"}       (dep->expressions ['org.activecomponents.jadex/jadex-distribution-minimal     {:deps/manifest :mvn :mvn/version "4.0.250"}])))
    (is (valid= #{"GPL-3.0-only"}       (dep->expressions ['org.activecomponents.jadex/jadex-kernel-application       {:deps/manifest :mvn :mvn/version "4.0.250"}])))
    (is (valid= #{"GPL-3.0-only"}       (dep->expressions ['org.activecomponents.jadex/jadex-kernel-base              {:deps/manifest :mvn :mvn/version "4.0.250"}])))
    (is (valid= #{"GPL-3.0-only"}       (dep->expressions ['org.activecomponents.jadex/jadex-kernel-bdiv3             {:deps/manifest :mvn :mvn/version "4.0.250"}])))
    (is (valid= #{"GPL-3.0-only"}       (dep->expressions ['org.activecomponents.jadex/jadex-kernel-bpmn              {:deps/manifest :mvn :mvn/version "4.0.250"}])))
    (is (valid= #{"GPL-3.0-only"}       (dep->expressions ['org.activecomponents.jadex/jadex-kernel-component         {:deps/manifest :mvn :mvn/version "4.0.250"}])))
    (is (valid= #{"GPL-3.0-only"}       (dep->expressions ['org.activecomponents.jadex/jadex-kernel-micro             {:deps/manifest :mvn :mvn/version "4.0.250"}])))
    (is (valid= #{"GPL-3.0-only"}       (dep->expressions ['org.activecomponents.jadex/jadex-kernel-microservice      {:deps/manifest :mvn :mvn/version "4.0.250"}])))
    (is (valid= #{"GPL-3.0-only"}       (dep->expressions ['org.activecomponents.jadex/jadex-kernel-model-bpmn        {:deps/manifest :mvn :mvn/version "4.0.250"}])))
    (is (valid= #{"GPL-3.0-only"}       (dep->expressions ['org.activecomponents.jadex/jadex-platform-base            {:deps/manifest :mvn :mvn/version "4.0.250"}])))
    (is (valid= #{"GPL-3.0-only"}       (dep->expressions ['org.activecomponents.jadex/jadex-platform-bridge          {:deps/manifest :mvn :mvn/version "4.0.250"}])))
    (is (valid= #{"GPL-3.0-only"}       (dep->expressions ['org.activecomponents.jadex/jadex-rules-eca                {:deps/manifest :mvn :mvn/version "4.0.250"}])))
    (is (valid= #{"GPL-3.0-only"}       (dep->expressions ['org.activecomponents.jadex/jadex-serialization-binary     {:deps/manifest :mvn :mvn/version "4.0.250"}])))
    (is (valid= #{"GPL-3.0-only"}       (dep->expressions ['org.activecomponents.jadex/jadex-serialization-json       {:deps/manifest :mvn :mvn/version "4.0.250"}])))
    (is (valid= #{"GPL-3.0-only"}       (dep->expressions ['org.activecomponents.jadex/jadex-serialization-traverser  {:deps/manifest :mvn :mvn/version "4.0.250"}])))
    (is (valid= #{"GPL-3.0-only"}       (dep->expressions ['org.activecomponents.jadex/jadex-serialization-xml        {:deps/manifest :mvn :mvn/version "4.0.250"}])))
    (is (valid= #{"GPL-3.0-only"}       (dep->expressions ['org.activecomponents.jadex/jadex-transport-base           {:deps/manifest :mvn :mvn/version "4.0.250"}])))
    (is (valid= #{"GPL-3.0-only"}       (dep->expressions ['org.activecomponents.jadex/jadex-transport-relay          {:deps/manifest :mvn :mvn/version "4.0.250"}])))
    (is (valid= #{"GPL-3.0-only"}       (dep->expressions ['org.activecomponents.jadex/jadex-transport-tcp            {:deps/manifest :mvn :mvn/version "4.0.250"}])))
    (is (valid= #{"GPL-3.0-only"}       (dep->expressions ['org.activecomponents.jadex/jadex-transport-websocket      {:deps/manifest :mvn :mvn/version "4.0.250"}])))
    (is (valid= #{"GPL-3.0-only"}       (dep->expressions ['org.activecomponents.jadex/jadex-util-bytecode            {:deps/manifest :mvn :mvn/version "4.0.250"}])))
    (is (valid= #{"GPL-3.0-only"}       (dep->expressions ['org.activecomponents.jadex/jadex-util-commons             {:deps/manifest :mvn :mvn/version "4.0.250"}])))
    (is (valid= #{"GPL-3.0-only"}       (dep->expressions ['org.activecomponents.jadex/jadex-util-concurrent          {:deps/manifest :mvn :mvn/version "4.0.250"}])))
    (is (valid= #{"GPL-3.0-only"}       (dep->expressions ['org.activecomponents.jadex/jadex-util-gui                 {:deps/manifest :mvn :mvn/version "4.0.250"}])))
    (is (valid= #{"GPL-3.0-only"}       (dep->expressions ['org.activecomponents.jadex/jadex-util-javaparser          {:deps/manifest :mvn :mvn/version "4.0.250"}])))
    (is (valid= #{"GPL-3.0-only"}       (dep->expressions ['org.activecomponents.jadex/jadex-util-nativetools         {:deps/manifest :mvn :mvn/version "4.0.250"}])))
    (is (valid= #{"GPL-3.0-only"}       (dep->expressions ['org.activecomponents.jadex/jadex-util-security            {:deps/manifest :mvn :mvn/version "4.0.250"}])))
    (is (valid= #{"MIT"}                (dep->expressions ['org.bouncycastle/bcpkix-jdk15on                           {:deps/manifest :mvn :mvn/version "1.70"}])))
    (is (valid= #{"MIT"}                (dep->expressions ['org.bouncycastle/bcprov-jdk15on                           {:deps/manifest :mvn :mvn/version "1.70"}])))
    (is (valid= #{"MIT"}                (dep->expressions ['org.bouncycastle/bcutil-jdk15on                           {:deps/manifest :mvn :mvn/version "1.70"}])))
    (is (valid= #{"EPL-1.0"}            (dep->expressions ['org.clojure/core.async                                    {:deps/manifest :mvn :mvn/version "1.5.648"}])))
    (is (valid= #{"EPL-1.0"}            (dep->expressions ['org.clojure/data.codec                                    {:deps/manifest :mvn :mvn/version "0.1.1"}])))
    (is (valid= #{"EPL-1.0"}            (dep->expressions ['org.clojure/data.json                                     {:deps/manifest :mvn :mvn/version "2.4.0"}])))
    (is (valid= #{"EPL-1.0"}            (dep->expressions ['org.clojure/data.priority-map                             {:deps/manifest :mvn :mvn/version "1.1.0"}])))
    (is (valid= #{"EPL-1.0"}            (dep->expressions ['org.clojure/data.xml                                      {:deps/manifest :mvn :mvn/version "0.0.8"}])))
    (is (valid= #{"EPL-1.0"}            (dep->expressions ['org.clojure/data.zip                                      {:deps/manifest :mvn :mvn/version "1.0.0"}])))
    (is (valid= #{"EPL-1.0"}            (dep->expressions ['org.clojure/java.classpath                                {:deps/manifest :mvn :mvn/version "1.0.0"}])))
    (is (valid= #{"EPL-1.0"}            (dep->expressions ['org.clojure/tools.analyzer                                {:deps/manifest :mvn :mvn/version "1.1.0"}])))
    (is (valid= #{"EPL-1.0"}            (dep->expressions ['org.clojure/tools.analyzer.jvm                            {:deps/manifest :mvn :mvn/version "1.2.2"}])))
    (is (valid= #{"EPL-1.0"}            (dep->expressions ['org.clojure/tools.cli                                     {:deps/manifest :mvn :mvn/version "1.0.206"}])))
    (is (valid= #{"EPL-1.0"}            (dep->expressions ['org.clojure/tools.deps.alpha                              {:deps/manifest :mvn :mvn/version "0.12.1090"}])))
    (is (valid= #{"EPL-1.0"}            (dep->expressions ['org.clojure/tools.gitlibs                                 {:deps/manifest :mvn :mvn/version "2.4.172"}])))
    (is (valid= #{"EPL-1.0"}            (dep->expressions ['org.clojure/tools.logging                                 {:deps/manifest :mvn :mvn/version "1.2.2"}])))
    (is (valid= #{"EPL-1.0"}            (dep->expressions ['org.clojure/tools.namespace                               {:deps/manifest :mvn :mvn/version "1.2.0"}])))
    (is (valid= #{"MIT"}                (dep->expressions ['org.codehaus.mojo/animal-sniffer-annotations              {:deps/manifest :mvn :mvn/version "1.20"}])))
    (is (valid= #{"Apache-2.0"}         (dep->expressions ['org.codehaus.plexus/plexus-cipher                         {:deps/manifest :mvn :mvn/version "2.0"}])))
    (is (valid= #{"Apache-2.0"}         (dep->expressions ['org.codehaus.plexus/plexus-classworlds                    {:deps/manifest :mvn :mvn/version "2.6.0"}])))
    (is (valid= #{"Apache-2.0"}         (dep->expressions ['org.codehaus.plexus/plexus-component-annotations          {:deps/manifest :mvn :mvn/version "2.1.0"}])))
    (is (valid= #{"Apache-2.0"}         (dep->expressions ['org.codehaus.plexus/plexus-interpolation                  {:deps/manifest :mvn :mvn/version "1.26"}])))
    (is (valid= #{"Apache-2.0"}         (dep->expressions ['org.codehaus.plexus/plexus-sec-dispatcher                 {:deps/manifest :mvn :mvn/version "2.0"}])))
    (is (valid= #{"EPL-1.0"}            (dep->expressions ['org.eclipse.sisu/org.eclipse.sisu.inject                  {:deps/manifest :mvn :mvn/version "0.3.5"}])))
    (is (valid= #{"EPL-1.0"}            (dep->expressions ['org.eclipse.sisu/org.eclipse.sisu.plexus                  {:deps/manifest :mvn :mvn/version "0.3.5"}])))
    (is (valid= #{"BSD-3-Clause"}       (dep->expressions ['org.hamcrest/hamcrest-core                                {:deps/manifest :mvn :mvn/version "2.2"}])))
    (is (valid= #{"Plexus"}             (dep->expressions ['org.jdom/jdom2                                            {:deps/manifest :mvn :mvn/version "2.0.6.1"}])))
    (is (valid= #{"BSD-3-Clause"}       (dep->expressions ['org.nanohttpd/nanohttpd                                   {:deps/manifest :mvn :mvn/version "2.3.1"}])))
    (is (valid= #{"BSD-3-Clause"}       (dep->expressions ['org.nanohttpd/nanohttpd-websocket                         {:deps/manifest :mvn :mvn/version "2.3.1"}])))
    (is (valid= #{"BSD-3-Clause"}       (dep->expressions ['org.ow2.asm/asm                                           {:deps/manifest :mvn :mvn/version "9.2"}])))
    (is (valid= #{"BSD-3-Clause"}       (dep->expressions ['org.ow2.asm/asm-analysis                                  {:deps/manifest :mvn :mvn/version "9.2"}])))
    (is (valid= #{"BSD-3-Clause"}       (dep->expressions ['org.ow2.asm/asm-tree                                      {:deps/manifest :mvn :mvn/version "9.2"}])))
    (is (valid= #{"BSD-3-Clause"}       (dep->expressions ['org.ow2.asm/asm-util                                      {:deps/manifest :mvn :mvn/version "9.2"}])))
    (is (valid= #{"MIT"}                (dep->expressions ['org.slf4j/jul-to-slf4j                                    {:deps/manifest :mvn :mvn/version "1.7.32"}])))
    (is (valid= #{"Apache-2.0"}         (dep->expressions ['org.slf4j/log4j-over-slf4j                                {:deps/manifest :mvn :mvn/version "1.7.32"}])))
    (is (valid= #{"MIT"}                (dep->expressions ['org.slf4j/slf4j-api                                       {:deps/manifest :mvn :mvn/version "1.7.32"}])))
    (is (valid= #{"MIT"}                (dep->expressions ['org.slf4j/slf4j-nop                                       {:deps/manifest :mvn :mvn/version "1.7.32"}])))
    (is (valid= #{"Apache-2.0"}         (dep->expressions ['org.sonatype.plexus/plexus-cipher                         {:deps/manifest :mvn :mvn/version "1.7"}])))
    (is (valid= #{"Apache-2.0"}         (dep->expressions ['org.sonatype.plexus/plexus-sec-dispatcher                 {:deps/manifest :mvn :mvn/version "1.4"}])))
    (is (valid= #{(lcis/public-domain)} (dep->expressions ['org.tukaani/xz                                            {:deps/manifest :mvn :mvn/version "1.9"}])))
    (is (valid= #{"Apache-2.0"}         (dep->expressions ['org.xerial.snappy/snappy-java                             {:deps/manifest :mvn :mvn/version "1.1.8.4"}])))
    (is (valid= #{"Apache-2.0"}         (dep->expressions ['software.amazon.ion/ion-java                              {:deps/manifest :mvn :mvn/version "1.0.0"}]))))
  (testing "Valid deps - no licenses in deployed artifacts"
    (is (nil? (dep->expressions ['slipset/deps-deploy         {:deps/manifest :mvn :mvn/version "0.2.0"}])))
    (is (nil? (dep->expressions ['borkdude/sci.impl.reflector {:deps/manifest :mvn :mvn/version "0.0.1"}]))))
  (testing "Valid deps - multi license"
    (is (valid= #{"EPL-1.0 OR LGPL-3.0-only"}                              (dep->expressions ['ch.qos.logback/logback-classic            {:deps/manifest :mvn :mvn/version "1.2.7"}])))
    (is (valid= #{"EPL-1.0 OR LGPL-3.0-only"}                              (dep->expressions ['ch.qos.logback/logback-core               {:deps/manifest :mvn :mvn/version "1.2.7"}])))
    (is (valid= #{"CDDL-1.1 OR GPL-2.0-only WITH Classpath-exception-2.0"} (dep->expressions ['javax.mail/mail                           {:deps/manifest :mvn :mvn/version "1.4.7"}])))
    (is (valid= #{"Apache-2.0 OR LGPL-2.1-or-later"}                       (dep->expressions ['net.java.dev.jna/jna-platform             {:deps/manifest :mvn :mvn/version "5.10.0"}])))
    (is (valid= #{"GPL-2.0-only WITH Classpath-exception-2.0 OR MIT"}      (dep->expressions ['org.checkerframework/checker-compat-qual  {:deps/manifest :mvn :mvn/version "2.5.5"}])))
    (is (valid= #{"CDDL-1.1 OR GPL-2.0-only WITH Classpath-exception-2.0"} (dep->expressions ['javax.xml.bind/jaxb-api                   {:deps/manifest :mvn :mvn/version "2.4.0-b180830.0359"}]))))
  (testing "Valid deps - Maven classifiers"
    (is (= #{"Apache-2.0 OR LGPL-3.0-only"} (dep->expressions ['com.github.jnr/jffi$native {:deps/manifest :mvn :mvn/version "1.3.12"}])))))

(defn- distinct-licenses-in-lib-map
  [lib-map-with-license-info]
  (when lib-map-with-license-info
    (some-> (seq (filter identity (mapcat #(keys (:lice-comb/license-info %)) (vals lib-map-with-license-info))))
            set)))

(deftest deps-expressions-test
  (testing "Nil and empty deps"
    (is (nil? (deps-expressions nil)))
    (is (= {} (deps-expressions {}))))
  (testing "Single deps"
    (is (valid= #{"EPL-1.0"}                    (distinct-licenses-in-lib-map (deps-expressions {'org.clojure/clojure {:deps/manifest :mvn :mvn/version "1.10.3"}}))))
    (is (valid= #{"EPL-1.0"}                    (distinct-licenses-in-lib-map (deps-expressions {'com.github.athos/clj-check {:deps/manifest :deps :git/sha "518d5a1cbfcd7c952f548e6dbfcb9a4a5faf9062" :deps/root (str gitlib-dir "/com.github.athos/clj-check")}}))))
    (is (valid= #{"Apache-2.0 OR LGPL-3.0-only"} (distinct-licenses-in-lib-map (deps-expressions {'com.github.jnr/jffi$native {:deps/manifest :mvn :mvn/version "1.3.12"}}))))
    (is (= (distinct-licenses-in-lib-map (deps-expressions {'com.github.jnr/jffi        {:deps/manifest :mvn :mvn/version "1.3.12"}}))
           (distinct-licenses-in-lib-map (deps-expressions {'com.github.jnr/jffi$native {:deps/manifest :mvn :mvn/version "1.3.12"}})))))
  (testing "Multiple deps"
    (is (valid= #{"EPL-1.0" "EPL-2.0" "MIT" "Apache-2.0"}
                (distinct-licenses-in-lib-map (deps-expressions {'org.clojure/clojure                                       {:deps/manifest :mvn :mvn/version "1.10.3"}
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
                                                                 'tolitius/xml-in                                           {:deps/manifest :mvn :mvn/version "0.1.1"}}))))
    (is (valid= #{"EPL-1.0" "EPL-2.0"}
                (distinct-licenses-in-lib-map (deps-expressions {'org.clojure/clojure                   {:deps/manifest :mvn :mvn/version "1.10.3"}
                                                                 'org.clojure/spec.alpha                {:deps/manifest :mvn :mvn/version "0.2.194"}
                                                                 'org.clojure/core.specs.alpha          {:deps/manifest :mvn :mvn/version "0.2.56"}
                                                                 'org.clojure/data.xml                  {:deps/manifest :mvn :mvn/version "0.2.0-alpha6"}
                                                                 'org.clojure/data.codec                {:deps/manifest :mvn :mvn/version "0.1.0"}
                                                                 'tigris/tigris                         {:deps/manifest :mvn :mvn/version "0.1.2"}
                                                                 'clj-xml-validation/clj-xml-validation {:deps/manifest :mvn :mvn/version "1.0.2"}
                                                                 'camel-snake-kebab/camel-snake-kebab   {:deps/manifest :mvn :mvn/version "0.4.2"}
                                                                 'tolitius/xml-in                       {:deps/manifest :mvn :mvn/version "0.1.1"}
                                                                 'com.github.athos/clj-check            {:deps/manifest :deps :git/sha "518d5a1cbfcd7c952f548e6dbfcb9a4a5faf9062" :deps/root (str gitlib-dir "/com.github.athos/clj-check")}})))))
  (testing "Deps with bad POMs"
    (is (nil? (distinct-licenses-in-lib-map (deps-expressions {'org.codehaus.plexus/plexus-container-default {:deps/manifest :mvn :mvn/version "1.0-alpha-9-stable-1"}}))))))
