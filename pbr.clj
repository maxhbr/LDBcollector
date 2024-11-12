;
; Copyright © 2021 Peter Monks
;
; This Source Code Form is subject to the terms of the Mozilla Public
; License, v. 2.0. If a copy of the MPL was not distributed with this
; file, You can obtain one at https://mozilla.org/MPL/2.0/.
;
; SPDX-License-Identifier: MPL-2.0
;

#_{:clj-kondo/ignore [:unresolved-namespace]}
(defn set-opts
  [opts]
  (assoc opts
         :lib          'com.github.pmonks/lice-comb
         :version      (pbr/calculate-version 2 0)
         :prod-branch  "release"
         :write-pom    true
         :validate-pom true
         :pom          {:description      "A Clojure library for software license detection."
                        :url              "https://github.com/pmonks/lice-comb"
                        :licenses         [:license   {:name "MPL-2.0" :url "https://www.mozilla.org/en-US/MPL/2.0/"}]
                        :developers       [:developer {:id "pmonks" :name "Peter Monks" :email "pmonks+lice-comb@gmail.com"}]
                        :scm              {:url "https://github.com/pmonks/lice-comb" :connection "scm:git:git://github.com/pmonks/lice-comb.git" :developer-connection "scm:git:ssh://git@github.com/pmonks/lice-comb.git"}
                        :issue-management {:system "github" :url "https://github.com/pmonks/lice-comb/issues"}}
         :codox        {:namespaces ['lice-comb.deps 'lice-comb.files 'lice-comb.lein 'lice-comb.matching 'lice-comb.maven 'lice-comb.utils]
                        :metadata   {:doc/format :markdown}
                        :doc-files  ["doc/overview.md"]}))
