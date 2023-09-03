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

(ns lice-comb.impl.metadata-test
  (:require [clojure.test               :refer [deftest testing is use-fixtures]]
            [lice-comb.test-boilerplate :refer [fixture]]
            [lice-comb.impl.metadata    :refer [prepend-source union]]))

(use-fixtures :once fixture)

(def md1 {
  "Apache-2.0" {:type :concluded :confidence :medium :strategy :regex-matching                     :source '("Apache Software Licence v2.0")}
  "MIT"        {:type :concluded :confidence :high   :strategy :spdx-listed-identifier-exact-match :source '("MIT")}
})

(def md2 {
  "Apache-2.0"   {:type :concluded :confidence :low  :strategy :regex-matching :source '("Apache style license")}
  "BSD-4-Clause" {:type :concluded :confidence :low  :strategy :regex-matching :source '("BSD")}
  })

(deftest prepend-source-tests
  (testing "nil/empty/blank"
    (is (nil?  (prepend-source nil nil)))
    (is (nil?  (prepend-source nil "")))
    (is (= #{} (prepend-source #{} nil)))
    (is (nil?  (meta (prepend-source #{} nil))))
    (is (= #{} (prepend-source #{} "")))
    (is (nil?  (meta (prepend-source #{} "")))))
  (testing "non-nil metadata that isn't lice-comb specific"
    (is (= {}           (meta (prepend-source (with-meta #{:a} {}) "foo"))))
    (is (= {:foo "foo"} (meta (prepend-source (with-meta #{:a} {:foo "foo"}) "bar"))))
  (testing "non-nil metadata that is lice-comb specific"
    (is (= {"Apache-2.0" {:type :concluded :confidence :medium :strategy :regex-matching                     :source '("pom.xml" "Apache Software Licence v2.0")}
            "MIT"        {:type :concluded :confidence :high   :strategy :spdx-listed-identifier-exact-match :source '("pom.xml" "MIT")}}
           (meta (prepend-source (with-meta #{:a} md1) "pom.xml"))))
    (is (= {"Apache-2.0" {:type :concluded :confidence :medium :strategy :regex-matching                     :source '("library.jar" "pom.xml" "Apache Software Licence v2.0")}
            "MIT"        {:type :concluded :confidence :high   :strategy :spdx-listed-identifier-exact-match :source '("library.jar" "pom.xml" "MIT")}}
           (meta (prepend-source (prepend-source (with-meta #{:a} md1) "pom.xml") "library.jar")))))))

(deftest union-tests
  (testing "zero arg"
    (is (= #{}            (union))))
  (testing "one arg"
    (is (nil?             (union nil)))
    (is (= #{}            (union #{})))
    (is (= #{:foo}        (union #{:foo}))))
  (testing "two arg"
    (is (= #{:foo :bar}   (union #{:foo} #{:bar}))))
  (testing "multi-arg"
    (is (= #{:a :b :c}    (union #{:a} #{:b} #{:c})))
    (is (= #{:a :b :c :d} (union #{:a} #{:b} #{:c} #{:d})))
    (is (= #{:a :b :c :d :e :f :g :h :i :j :k :l :m :n :o} (union #{:a :b} #{:c :d :e} #{:f :g :h :i} #{:j :k :l :m :n :o}))))
  (testing "metadata"
    (is (= {:foo "foo"}                         (meta (union (with-meta #{:a :b :c} {:foo "foo"})))))
    (is (= {:foo "foo" :bar "bar"}              (meta (union (with-meta #{:a :b :c} {:foo "foo"}) (with-meta #{:d :e :f} {:bar "bar"})))))
    (is (= {:foo "foo" :bar "bar" :blah "blah"} (meta (union (with-meta #{:a :b :c} {:foo "foo"}) (with-meta #{:d :e :f} {:bar "bar"}) (with-meta #{:g :h :i} {:blah "blah"})))))
    (is (thrown? clojure.lang.ExceptionInfo     (meta (union (with-meta #{:a :b :c} {:foo "foo"}) (with-meta #{:d :e :f} {:foo "bar"})))))  ; Non lice-comb conflicting key in metadata maps = exception
    (is (= {"Apache-2.0"   {:type :concluded :confidence :medium :strategy :regex-matching                     :source '("Apache Software Licence v2.0")}
            "MIT"          {:type :concluded :confidence :high   :strategy :spdx-listed-identifier-exact-match :source '("MIT")}
            "BSD-4-Clause" {:type :concluded :confidence :low    :strategy :regex-matching                     :source '("BSD")}
           }
           (meta (union (with-meta #{:a :b :c} md1) (with-meta #{:d :e :f} md2)))))))

