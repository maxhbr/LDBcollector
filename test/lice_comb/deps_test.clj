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
  (testing "Unknown dep types"
    (is (thrown? clojure.lang.ExceptionInfo (dep->ids ['com.github.pmonks/lice-comb {:deps/manifest :invalid :mvn/version "1.0.0"}]))))
  (testing "Invalid deps"
    (is (nil? (dep->ids ['com.github.pmonks/invalid-project {:deps/manifest :mvn :mvn/version "0.0.1"}])))  ; Invalid GA
    (is (nil? (dep->ids ['org.clojure/clojure {:deps/manifest :mvn :mvn/version "1.0.0-SNAPSHOT"}]))))      ; Invalid V
  (testing "Valid deps - single license"
    (is (= #{"Apache-2.0"}             (dep->ids ['com.github.pmonks/asf-cat {:deps/manifest :mvn :mvn/version "1.0.12"}])))
    (is (= #{"EPL-1.0"}                (dep->ids ['org.clojure/clojure {:deps/manifest :mvn :mvn/version "1.10.3"}])))
    (is (= #{"EPL-1.0"}                (dep->ids ['com.github.athos/clj-check {:deps/manifest :deps :deps/root (str gitlib-dir "/com.github.athos/clj-check") :lice-comb/licenses #{"EPL-1.0"}}])))
    (is (= #{"BSD-3-Clause"}           (dep->ids ['org.ow2.asm/asm {:deps/manifest :mvn :mvn/version "5.2"}])))
    (is (= #{"NON-SPDX-Public-Domain"} (dep->ids ['aopalliance/aopalliance {:deps/manifest :mvn :mvn/version "1.0"}])))
    (is (= #{"Apache-2.0"}             (dep->ids ['com.amazonaws/aws-java-sdk-core {:deps/manifest :mvn :mvn/version "1.12.129"}])))
    (is (= #{"Apache-2.0"}             (dep->ids ['com.amazonaws/aws-java-sdk-kms {:deps/manifest :mvn :mvn/version "1.12.129"}])))
    (is (= #{"Apache-2.0"}             (dep->ids ['com.amazonaws/aws-java-sdk-s3 {:deps/manifest :mvn :mvn/version "1.12.129"}])))
    (is (= #{"Apache-2.0"}             (dep->ids ['com.amazonaws/aws-java-sdk-sts {:deps/manifest :mvn :mvn/version "1.12.129"}])))
    (is (= #{"Apache-2.0"}             (dep->ids ['com.fasterxml.jackson.dataformat/jackson-dataformat-cbor {:deps/manifest :mvn :mvn/version "2.13.0"}])))
    (is (= #{"Apache-2.0"}             (dep->ids ['com.fasterxml.jackson.dataformat/jackson-dataformat-smile {:deps/manifest :mvn :mvn/version "2.13.0"}])))
    (is (= #{"Apache-2.0"}             (dep->ids ['com.google.guava/guava {:deps/manifest :mvn :mvn/version "31.0.1-jre"}])))
    (is (= #{"Apache-2.0"}             (dep->ids ['io.opentracing/opentracing-api {:deps/manifest :mvn :mvn/version "0.33.0"}])))
    (is (= #{"Apache-2.0"}             (dep->ids ['io.opentracing/opentracing-mock {:deps/manifest :mvn :mvn/version "0.33.0"}])))
    (is (= #{"Apache-2.0"}             (dep->ids ['io.opentracing/opentracing-noop {:deps/manifest :mvn :mvn/version "0.33.0"}])))
    (is (= #{"Apache-2.0"}             (dep->ids ['io.opentracing/opentracing-util {:deps/manifest :mvn :mvn/version "0.33.0"}])))
    (is (= #{"CDDL-1.0"}               (dep->ids ['javax.activation/activation {:deps/manifest :mvn :mvn/version "1.1.1"}])))
    (is (= #{"CDDL-1.0"}               (dep->ids ['javax.annotation/jsr250-api {:deps/manifest :mvn :mvn/version "1.0"}])))
    (is (= #{"Apache-2.0"}             (dep->ids ['javax.enterprise/cdi-api {:deps/manifest :mvn :mvn/version "2.0"}])))
    (is (= #{"Apache-2.0"}             (dep->ids ['javax.inject/javax.inject {:deps/manifest :mvn :mvn/version "1"}])))
    (is (= #{"EPL-1.0"}                (dep->ids ['junit/junit {:deps/manifest :mvn :mvn/version "4.13.2"}])))
    (is (= #{"CC0-1.0"}                (dep->ids ['net.i2p.crypto/eddsa {:deps/manifest :mvn :mvn/version "0.3.0"}])))
    (is (= #{"Apache-2.0"}             (dep->ids ['net.jpountz.lz4/lz4 {:deps/manifest :mvn :mvn/version "1.3.0"}])))
    (is (= #{"GPL-3.0"}                (dep->ids ['org.activecomponents.jadex/jadex-distribution-minimal {:deps/manifest :mvn :mvn/version "4.0.250"}])))
    (is (= #{"GPL-3.0"}                (dep->ids ['org.activecomponents.jadex/jadex-kernel-application {:deps/manifest :mvn :mvn/version "4.0.250"}])))
    (is (= #{"GPL-3.0"}                (dep->ids ['org.activecomponents.jadex/jadex-kernel-base {:deps/manifest :mvn :mvn/version "4.0.250"}])))
    (is (= #{"GPL-3.0"}                (dep->ids ['org.activecomponents.jadex/jadex-kernel-bdiv3 {:deps/manifest :mvn :mvn/version "4.0.250"}])))
    (is (= #{"GPL-3.0"}                (dep->ids ['org.activecomponents.jadex/jadex-kernel-bpmn {:deps/manifest :mvn :mvn/version "4.0.250"}])))
    (is (= #{"GPL-3.0"}                (dep->ids ['org.activecomponents.jadex/jadex-kernel-component {:deps/manifest :mvn :mvn/version "4.0.250"}])))
    (is (= #{"GPL-3.0"}                (dep->ids ['org.activecomponents.jadex/jadex-kernel-micro {:deps/manifest :mvn :mvn/version "4.0.250"}])))
    (is (= #{"GPL-3.0"}                (dep->ids ['org.activecomponents.jadex/jadex-kernel-microservice {:deps/manifest :mvn :mvn/version "4.0.250"}])))
    (is (= #{"GPL-3.0"}                (dep->ids ['org.activecomponents.jadex/jadex-kernel-model-bpmn {:deps/manifest :mvn :mvn/version "4.0.250"}])))
    (is (= #{"GPL-3.0"}                (dep->ids ['org.activecomponents.jadex/jadex-platform-base {:deps/manifest :mvn :mvn/version "4.0.250"}])))
    (is (= #{"GPL-3.0"}                (dep->ids ['org.activecomponents.jadex/jadex-platform-bridge {:deps/manifest :mvn :mvn/version "4.0.250"}])))
    (is (= #{"GPL-3.0"}                (dep->ids ['org.activecomponents.jadex/jadex-rules-eca {:deps/manifest :mvn :mvn/version "4.0.250"}])))
    (is (= #{"GPL-3.0"}                (dep->ids ['org.activecomponents.jadex/jadex-serialization-binary {:deps/manifest :mvn :mvn/version "4.0.250"}])))
    (is (= #{"GPL-3.0"}                (dep->ids ['org.activecomponents.jadex/jadex-serialization-json {:deps/manifest :mvn :mvn/version "4.0.250"}])))
    (is (= #{"GPL-3.0"}                (dep->ids ['org.activecomponents.jadex/jadex-serialization-traverser {:deps/manifest :mvn :mvn/version "4.0.250"}])))
    (is (= #{"GPL-3.0"}                (dep->ids ['org.activecomponents.jadex/jadex-serialization-xml {:deps/manifest :mvn :mvn/version "4.0.250"}])))
    (is (= #{"GPL-3.0"}                (dep->ids ['org.activecomponents.jadex/jadex-transport-base {:deps/manifest :mvn :mvn/version "4.0.250"}])))
    (is (= #{"GPL-3.0"}                (dep->ids ['org.activecomponents.jadex/jadex-transport-relay {:deps/manifest :mvn :mvn/version "4.0.250"}])))
    (is (= #{"GPL-3.0"}                (dep->ids ['org.activecomponents.jadex/jadex-transport-tcp {:deps/manifest :mvn :mvn/version "4.0.250"}])))
    (is (= #{"GPL-3.0"}                (dep->ids ['org.activecomponents.jadex/jadex-transport-websocket {:deps/manifest :mvn :mvn/version "4.0.250"}])))
    (is (= #{"GPL-3.0"}                (dep->ids ['org.activecomponents.jadex/jadex-util-bytecode {:deps/manifest :mvn :mvn/version "4.0.250"}])))
    (is (= #{"GPL-3.0"}                (dep->ids ['org.activecomponents.jadex/jadex-util-commons {:deps/manifest :mvn :mvn/version "4.0.250"}])))
    (is (= #{"GPL-3.0"}                (dep->ids ['org.activecomponents.jadex/jadex-util-concurrent {:deps/manifest :mvn :mvn/version "4.0.250"}])))
    (is (= #{"GPL-3.0"}                (dep->ids ['org.activecomponents.jadex/jadex-util-gui {:deps/manifest :mvn :mvn/version "4.0.250"}])))
    (is (= #{"GPL-3.0"}                (dep->ids ['org.activecomponents.jadex/jadex-util-javaparser {:deps/manifest :mvn :mvn/version "4.0.250"}])))
    (is (= #{"GPL-3.0"}                (dep->ids ['org.activecomponents.jadex/jadex-util-nativetools {:deps/manifest :mvn :mvn/version "4.0.250"}])))
    (is (= #{"GPL-3.0"}                (dep->ids ['org.activecomponents.jadex/jadex-util-security {:deps/manifest :mvn :mvn/version "4.0.250"}])))
    (is (= #{"MIT"}                    (dep->ids ['org.bouncycastle/bcpkix-jdk15on {:deps/manifest :mvn :mvn/version "1.70"}])))
    (is (= #{"MIT"}                    (dep->ids ['org.bouncycastle/bcprov-jdk15on {:deps/manifest :mvn :mvn/version "1.70"}])))
    (is (= #{"MIT"}                    (dep->ids ['org.bouncycastle/bcutil-jdk15on {:deps/manifest :mvn :mvn/version "1.70"}])))
    (is (= #{"EPL-1.0"}                (dep->ids ['org.clojure/core.async {:deps/manifest :mvn :mvn/version "1.5.648"}])))
    (is (= #{"EPL-1.0"}                (dep->ids ['org.clojure/data.codec {:deps/manifest :mvn :mvn/version "0.1.1"}])))
    (is (= #{"EPL-1.0"}                (dep->ids ['org.clojure/data.json {:deps/manifest :mvn :mvn/version "2.4.0"}])))
    (is (= #{"EPL-1.0"}                (dep->ids ['org.clojure/data.priority-map {:deps/manifest :mvn :mvn/version "1.1.0"}])))
    (is (= #{"EPL-1.0"}                (dep->ids ['org.clojure/data.xml {:deps/manifest :mvn :mvn/version "0.0.8"}])))
    (is (= #{"EPL-1.0"}                (dep->ids ['org.clojure/data.zip {:deps/manifest :mvn :mvn/version "1.0.0"}])))
    (is (= #{"EPL-1.0"}                (dep->ids ['org.clojure/java.classpath {:deps/manifest :mvn :mvn/version "1.0.0"}])))
    (is (= #{"EPL-1.0"}                (dep->ids ['org.clojure/tools.analyzer {:deps/manifest :mvn :mvn/version "1.1.0"}])))
    (is (= #{"EPL-1.0"}                (dep->ids ['org.clojure/tools.analyzer.jvm {:deps/manifest :mvn :mvn/version "1.2.2"}])))
    (is (= #{"EPL-1.0"}                (dep->ids ['org.clojure/tools.cli {:deps/manifest :mvn :mvn/version "1.0.206"}])))
    (is (= #{"EPL-1.0"}                (dep->ids ['org.clojure/tools.deps.alpha {:deps/manifest :mvn :mvn/version "0.12.1090"}])))
    (is (= #{"EPL-1.0"}                (dep->ids ['org.clojure/tools.gitlibs {:deps/manifest :mvn :mvn/version "2.4.172"}])))
    (is (= #{"EPL-1.0"}                (dep->ids ['org.clojure/tools.logging {:deps/manifest :mvn :mvn/version "1.2.2"}])))
    (is (= #{"EPL-1.0"}                (dep->ids ['org.clojure/tools.namespace {:deps/manifest :mvn :mvn/version "1.2.0"}])))
    (is (= #{"MIT"}                    (dep->ids ['org.codehaus.mojo/animal-sniffer-annotations {:deps/manifest :mvn :mvn/version "1.20"}])))
    (is (= #{"Apache-2.0"}             (dep->ids ['org.codehaus.plexus/plexus-cipher {:deps/manifest :mvn :mvn/version "2.0"}])))
    (is (= #{"Apache-2.0"}             (dep->ids ['org.codehaus.plexus/plexus-classworlds {:deps/manifest :mvn :mvn/version "2.6.0"}])))
    (is (= #{"Apache-2.0"}             (dep->ids ['org.codehaus.plexus/plexus-component-annotations {:deps/manifest :mvn :mvn/version "2.1.0"}])))
    (is (= #{"Apache-2.0"}             (dep->ids ['org.codehaus.plexus/plexus-interpolation {:deps/manifest :mvn :mvn/version "1.26"}])))
    (is (= #{"Apache-2.0"}             (dep->ids ['org.codehaus.plexus/plexus-sec-dispatcher {:deps/manifest :mvn :mvn/version "2.0"}])))
    (is (= #{"EPL-1.0"}                (dep->ids ['org.eclipse.sisu/org.eclipse.sisu.inject {:deps/manifest :mvn :mvn/version "0.3.5"}])))
    (is (= #{"EPL-1.0"}                (dep->ids ['org.eclipse.sisu/org.eclipse.sisu.plexus {:deps/manifest :mvn :mvn/version "0.3.5"}])))
    (is (= #{"BSD-3-Clause"}           (dep->ids ['org.hamcrest/hamcrest-core {:deps/manifest :mvn :mvn/version "2.2"}])))
    (is (= #{"Plexus"}                 (dep->ids ['org.jdom/jdom2 {:deps/manifest :mvn :mvn/version "2.0.6.1"}])))
    (is (= #{"BSD-3-Clause"}           (dep->ids ['org.nanohttpd/nanohttpd {:deps/manifest :mvn :mvn/version "2.3.1"}])))
    (is (= #{"BSD-3-Clause"}           (dep->ids ['org.nanohttpd/nanohttpd-websocket {:deps/manifest :mvn :mvn/version "2.3.1"}])))
    (is (= #{"BSD-3-Clause"}           (dep->ids ['org.ow2.asm/asm {:deps/manifest :mvn :mvn/version "9.2"}])))
    (is (= #{"BSD-3-Clause"}           (dep->ids ['org.ow2.asm/asm-analysis {:deps/manifest :mvn :mvn/version "9.2"}])))
    (is (= #{"BSD-3-Clause"}           (dep->ids ['org.ow2.asm/asm-tree {:deps/manifest :mvn :mvn/version "9.2"}])))
    (is (= #{"BSD-3-Clause"}           (dep->ids ['org.ow2.asm/asm-util {:deps/manifest :mvn :mvn/version "9.2"}])))
    (is (= #{"MIT"}                    (dep->ids ['org.slf4j/jul-to-slf4j {:deps/manifest :mvn :mvn/version "1.7.32"}])))
    (is (= #{"Apache-2.0"}             (dep->ids ['org.slf4j/log4j-over-slf4j {:deps/manifest :mvn :mvn/version "1.7.32"}])))
    (is (= #{"MIT"}                    (dep->ids ['org.slf4j/slf4j-api {:deps/manifest :mvn :mvn/version "1.7.32"}])))
    (is (= #{"MIT"}                    (dep->ids ['org.slf4j/slf4j-nop {:deps/manifest :mvn :mvn/version "1.7.32"}])))
    (is (= #{"Apache-2.0"}             (dep->ids ['org.sonatype.plexus/plexus-cipher {:deps/manifest :mvn :mvn/version "1.7"}])))
    (is (= #{"Apache-2.0"}             (dep->ids ['org.sonatype.plexus/plexus-sec-dispatcher {:deps/manifest :mvn :mvn/version "1.4"}])))
    (is (= #{"NON-SPDX-Public-Domain"} (dep->ids ['org.tukaani/xz {:deps/manifest :mvn :mvn/version "1.9"}])))
    (is (= #{"Apache-2.0"}             (dep->ids ['org.xerial.snappy/snappy-java {:deps/manifest :mvn :mvn/version "1.1.8.4"}])))
    (is (= #{"Apache-2.0"}             (dep->ids ['software.amazon.ion/ion-java {:deps/manifest :mvn :mvn/version "1.0.0"}]))))
  (testing "Valid deps - no licenses in deployed artifacts -> leverage fallbacks"
    (is (= #{"EPL-1.0"} (dep->ids ['slipset/deps-deploy         {:deps/manifest :mvn :mvn/version "0.2.0"}])))
    (is (= #{"EPL-1.0"} (dep->ids ['borkdude/sci.impl.reflector {:deps/manifest :mvn :mvn/version "0.0.1"}]))))
  (testing "Valid deps - multi license"
    (is (= #{"EPL-1.0" "LGPL-2.1"}                          (dep->ids ['ch.qos.logback/logback-classic {:deps/manifest :mvn :mvn/version "1.2.7"}])))
    (is (= #{"EPL-1.0" "LGPL-2.1"}                          (dep->ids ['ch.qos.logback/logback-core {:deps/manifest :mvn :mvn/version "1.2.7"}])))
    (is (= #{"CDDL-1.1" "GPL-2.0-with-classpath-exception"} (dep->ids ['javax.mail/mail {:deps/manifest :mvn :mvn/version "1.4.7"}])))
    (is (= #{"Apache-2.0" "LGPL-2.1-or-later"}              (dep->ids ['net.java.dev.jna/jna-platform {:deps/manifest :mvn :mvn/version "5.10.0"}])))
    (is (= #{"GPL-2.0-with-classpath-exception" "MIT"}      (dep->ids ['org.checkerframework/checker-compat-qual {:deps/manifest :mvn :mvn/version "2.5.5"}])))))

(deftest deps-licenses-test
  (testing "Nil and empty deps"
    (is (nil? (deps-licenses nil)))
    (is (= {} (deps-licenses {}))))
  (testing "Single deps"
    (is (= #{"EPL-1.0"} (:lice-comb/licenses (get (deps-licenses {'org.clojure/clojure {:deps/manifest :mvn :mvn/version "1.10.3"}}) 'org.clojure/clojure))))
    (is (= #{"EPL-1.0"} (:lice-comb/licenses (get (deps-licenses {'com.github.athos/clj-check {:deps/manifest :deps :deps/root (str gitlib-dir "/com.github.athos/clj-check")}}) 'com.github.athos/clj-check)))))    ; Note: we use this git dep, as it's used earlier in the build, so we can be sure it's been downloaded before this test is run
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
