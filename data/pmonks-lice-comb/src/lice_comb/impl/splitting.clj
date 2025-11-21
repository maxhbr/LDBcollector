;
; Copyright © 2024 Peter Monks
;
; This Source Code Form is subject to the terms of the Mozilla Public
; License, v. 2.0. If a copy of the MPL was not distributed with this
; file, You can obtain one at https://mozilla.org/MPL/2.0/.
;
; SPDX-License-Identifier: MPL-2.0
;

(ns lice-comb.impl.splitting
  "Splitting helper functionality. Note: this namespace is not part of
  the public API of lice-comb and may change without notice."
  (:require [clojure.string       :as s]
            [lice-comb.impl.utils :as lciu]))

(def op-re          #"\s+(and[/\-\\]or|and|&|or|w/|with|\s+)+\s+")
(def leading-op-re  (lciu/re-concat "(?i)\\A" op-re))
(def trailing-op-re (lciu/re-concat "(?i)" op-re "\\z"))

(defn strip-leading-and-trailing-operators
  "Strips all leading and trailing operators (and, or, and/or, with) from `s`."
  [s]
  (when s
    (let [new-s (-> (str " " s " ")   ; Ensure s has leading and trailing whitespace, as op-re requires it to exist
                    (s/replace leading-op-re  "")
                    (s/replace trailing-op-re ""))]
      (when-not (s/blank? new-s)
        (s/trim new-s)))))

(def ^:private and-or-splitting-re           #"(?i)(?<=\s)and[/\-\\]or(?=\s)")
(def ^:private abbreviated-with-splitting-re #"(?i)\bw/")
(def ^:private abbreviated-and-splitting-re  #"(?i)&")
(def ^:private and-or-with-splitting-re      #"(?i)\b((and|&)(?![/\-\\]or)|(?<!(and|&)[/\-\\])or|with)\b")

(defn- naive-operator-split
  "Naively splits `s` (a `String`) on potential operators. Returns a sequence
  (potentially of one element), or `nil` if `s` is `nil`."
  [s]
  (when s
    (->> (lciu/retained-split (strip-leading-and-trailing-operators s) and-or-splitting-re)
         (mapcat #(lciu/retained-split % abbreviated-with-splitting-re))
         (mapcat #(lciu/retained-split % abbreviated-and-splitting-re))
         (mapcat #(lciu/retained-split % and-or-with-splitting-re)))))

(defn- tag-operators
  "Tags potential operators in `coll` (a sequence of `String`s), by turning
  them into tuples of `[keyword original-value]`.  The keywords are:
  * :and
  * :or
  * :with
  * :and-or"
  [coll]
  (map #(case (s/lower-case %)
          ("and" "&")                   [:and    %]
          "or"                          [:or     %]
          ("with" "w/")                 [:with   %]
          ("and/or" "and-or" "and\\or") [:and-or %]
          %)
       coll))

(defn- any-re-pairs-match?
  "Do any of the regular expression pairs in `re-pairs` match `before-text` (1st
  regular expression in the pair) and also `after-text` (2nd regular expression
  in the pair)?"
  [before-text after-text re-pairs]
  (boolean (some identity (map #(and (re-find (first %)  before-text)
                                     (re-find (second %) after-text))
                               re-pairs))))

;####TODO: build these programmatically from the SPDX license and exception lists
; Relevant names can be found with this code:
;    (let [all-names      (concat (map :name @lcis/license-list-d) (map :name @lcis/exception-list-d))
;          relevant-names (filter #(> (count %) 1) (map naive-operator-split all-names))]

(def ^:private re-and-before-after-pairs [
  ; :and operator checks
  [#"(?i)\bcopyright\s*\z"                                                            #"(?i)\A\s*all\s+rights\s+reserved\b"]
  [#"(?i)\bcommon\s+development\s*\z"                                                 #"(?i)\A\s*distribution\s+licen[cs]e\b"]
  [#"(?i)\bBSD\s+with\s+attribution\s*\z"                                             #"(?i)\A\s*HPND\s+disclaimer\b"]
  [#"(?i)\bHistorical\s+Permission\s+Notice\s*\z"                                     #"(?i)\A\s*Disclaimer\b"]
  [#"(?i)\bHPND\s+with\s+US\s+Government\s+export\s+control\s+warning\s*\z"           #"(?i)\A\s*(acknowledgment|modification)\b"]
  [#"(?i)\bHistorical\s+Permission\s+Notice\s*\z"                                     #"(?i)\A\s*Disclaimer\b"]
  [#"(?i)\bIBM\s+PowerPC\s+Initialization\s*\z"                                       #"(?i)\A\s*Boot\s+Software\b"]
  [#"(?i)\bLZMA\s+SDK\s+Licen[cs]e\s+\(?versions?\s+\d\.\d\d\s*\z"                    #"(?i)\A\s*beyond\)?\b"]
  [#"(?i)\bNara\s+Institute\s+of\s+Science\s*\z"                                      #"(?i)\A\s*Technology\s+Licen[cs]e\b"]
  [#"(?i)\bOpen\s+LDAP\s+Public\s+Licen[cs]e\s+v2\.0\s+\(?or\s+possibly\s+2\.0A\s*\z" #"(?i)\A\s*2.0B\)?\b"]
  [#"(?i)\bUnicode\s+Licen[cs]e\s+Agreement\s+[\-\s]*Data\s+Files\s*\z"               #"(?i)\A\s*Software\b"]
  [#"(?i)\bW3C\s+Software\s+Notice\s*\z"                                              #"(?i)\A\s*(Document\s+)?Licen[cs]e\b"]
  [#"(?i)\bbzip2\s*\z"                                                                #"(?i)\A\s*libbzip2\s+Licen[cs]e\b"]])

(defn- non-operator-and-within-text?
  "Was there a a non-operator use of `and` between the two texts?"
  [before-text after-text]
  (any-re-pairs-match? before-text after-text re-and-before-after-pairs))

(def ^:private re-or-before-after-pairs [
  ; Original regexes
  [#"(?i).+\z"                                                  #"(?i)\A[\s\-]*(greater|(any\s+)?lat[eo]r|(any\s+)?newer|\(?at\s+your\s+(option|discretion)\)?|([\"']?(Revised|Modified)[\"']?))"]
  [#"(?i)\blesser\s*\z"                                         #"(?i)\A[\s\-]*library\b"]
  [#"(?i)\blibrary\s*\z"                                        #"(?i)\A[\s\-]*lesser\b"]
  ; Names from SPDX license list
  [#"(?i)\bBSD\s+3-Clause\s+\"?New\"?\s*\z"                     #"(?i)\A\s*\"?Revised\"?\s+Licen[cs]e\b"]
  [#"(?i)\bBSD\s+4-Clause\s+\"?Original\"?\s*\z"                #"(?i)\A\s*\"?Old\"?\s+Licen[cs]e\b"]
  [#"(?i)\bOpen\s+LDAP\s+Public\s+Licen[cs]e\s+v2\.0\s+\(\s*\z" #"(?i)\A\s*possibly\s+2\.0A\b"]])

(defn- non-operator-or-within-text?
  "Was there a a non-operator use of `or` between the two texts?"
  [before-text after-text]
  (any-re-pairs-match? before-text after-text re-or-before-after-pairs))

(def ^:private re-with-before-after-pairs [
  ; Original regexes
  [#"(?i).+\z"                                                                                         #"(?i)\A\s*the\s+acknowledgment\s+clause\s+removed"]
  ; Names from SPDX license list
  [#"(?i)\bBSD\s*\z"                                                                                   #"(?i)\A\s*Attribution\b"]
  [#"(?i)\bFSF\s+Unlimited\s+Licen[cs]e(\s+\()?\s*\z"                                                  #"(?i)\A\s*Licen[cs]e\s+Retention\b"]
  [#"(?i)\bGood\s+Luck\s*\z"                                                                           #"(?i)\A\s*That\s+Public\s+Licen[cs]e\b"]
  [#"(?i)\bHPND\s*\z"                                                                                  #"(?i)\A\s*US\s+Government\s+export\s+control\b"]
  [#"(?i)\bHPND\s+sell\s+variant\s*\z"                                                                 #"(?i)\A\s*MIT\s+disclaimer\b"]
  [#"(?i)\bHistorical\s+Permission\s+Notice\s+and\s+Disclaimer(\s+-\s+sell\s+xserver\s+variant)?\s*\z" #"(?i)\A\s*MIT\s+disclaimer\b"]
  [#"(?i)\bANTLR\s+Software\s+Rights\s+Notice\s*\z"                                                    #"(?i)\A\s*licen[cs]e\s+fallback\b"]
  [#"(?i)\bLatex2e\s*\z"                                                                               #"(?i)\A\s*translated\s+notice\s+permission\b"]
  [#"(?i)\bNIST\s+Public\s+Domain\s+Notice\s*\z"                                                       #"(?i)\A\s*licen[cs]e\s+fallback\b"]
  [#"(?i)\bSIL\s+Open\s+Font\s+Licen[cs]e\s+\d+\.\d+\s*\z"                                             #"(?i)\A\s*(no\s+)?Reserved\s+Font\s+Name\b"]
  [#"(?i)\bzlib/libpng\s+Licen[cs]e\s*\z"                                                              #"(?i)\A\s*Acknowledgement\b"]])

(defn- non-operator-with-within-text?
  "Was there a a non-operator use of `with` between the two texts?"
  [before-text after-text]
  (any-re-pairs-match? before-text after-text re-with-before-after-pairs))

(defn- invalid-operator?
  "Returns `true` if an invalid operator was identified.  Examples include:
  * `GNU Lesser or Library Public License`
  * `Common Development and Distribution License`"
  [before-text op after-text]
  (case op
    :and  (non-operator-and-within-text?  before-text after-text)
    :or   (non-operator-or-within-text?   before-text after-text)
    :with (non-operator-with-within-text? before-text after-text)
    false))

(defn- validate-operators
  "Validates operators (identified in `coll` as a tuple - see
  `identify-operators` for details), by either:
  * replacing it with its associated keyword, if it's a valid operator
  * recombining it with its neighboring values, if it's not a valid operator
    (e.g. `[\"GNU Lesser \" [:or \"or\"] \" Library Public License\"]`)
  * removing it if it's an :and-or"
  [coll]
  (loop [result      []
         before-text (first coll)
         op          (second coll)
         after-text  (nth coll 2 nil)
         r           (nthrest coll 3)]
    (if-not before-text
      ; Base case - clean result and return
      (map #(if (string? %) (s/trim %) %) result)
      ; Recursive case
      (if (string? after-text)
        ; Normal case: string op string
        (let [[op-kw op-str] op]
          (if (invalid-operator? before-text op-kw after-text)
            (let [new-before-text (str before-text op-str after-text)  ; not a valid operator, so recombine the before and after text
                  new-result      (conj (vec (take (dec (count result)) result)) new-before-text)]
              (recur new-result new-before-text (first r) (second r) (nthrest r 2)))
            (let [new-result (if (= op-kw :and-or)
                               (concat result [before-text after-text])          ; and/or "operator", so drop the operator but retain the split
                               (concat result [before-text op-kw after-text]))]  ; valid operator, so insert the operator's keyword
              (recur new-result after-text (first r) (second r) (nthrest r 2)))))

        ; Unusual case: string op op
        (recur (conj (vec result) before-text) (nth r 2 nil) (nth r 3 nil) (nth r 4 nil) (nthrest r 4))))))

(def ^:private cursed-re #"(?i)(?<=CDDL)/(?=GPL)")   ; Special case for splitting particularly cursed combos such as CDDL/GPLv2+CE)

(defn- split-cursed
  "Split any strings in `coll` that contain particularly cursed values."
  [coll]
  (mapcat #(if (string? %)
             (s/split % cursed-re)
             [%])
          coll))

(defn- filter-blank-strings
  "Removes blank strings from `coll`, but keeps everything else, including 
  elements that are not strings."
  [coll]
  (filter #(or (not (string? %)) (not (s/blank? %))) coll))

(defn split-on-operators
  "Case insensitively splits a string based on license operators (and,
  or, with), but only if they're not also part of a license name (e.g.
  'Common Development and Distribution License', 'GNU General Public
  License version 2.0 or (at your option) any later version', etc.)."
  [s]
  (when-not (s/blank? s)
    (->> s
         naive-operator-split
         tag-operators
         validate-operators
         split-cursed
         filter-blank-strings
         dedupe)))
