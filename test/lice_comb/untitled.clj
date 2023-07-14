(defn re-named-groups
  "Returns a sequence of the names of all of the named capturing groups in the
  given regular expression, or nil if there are none.

  Note: workaround for https://bugs.openjdk.org/browse/JDK-7032377 (fixed
  in JDK 20)"
  [re]
  (seq (map second (re-seq #"\(\?<([a-zA-Z][a-zA-Z0-9]*)>" (str re)))))


(defn re-matches-ncg
  "Returns the match, if any, of string to pattern, using
  java.util.regex.Matcher.matches(). Returns a (potentially
  empty) map of the named-capturing groups in the regex if there
  was a match, or nil otherwise. Each key in the map is the name
  of a name-capturing group, and each value is the corresponding
  value in the string that matched that group."
  [re s]
  (let [matcher (re-matcher re s)]
    (when (.matches matcher)
      (let [ncgs (re-named-groups re)]
        (loop [result {}
               f      (first ncgs)
               r      (rest ncgs)]
          (if f
            (let [v (try (.group matcher f) (catch java.lang.IllegalArgumentException _ nil))]
              (recur (merge result (when v {f v}))
                     (first r)
                     (rest r)))
            result))))))


(re-matches-ncg #"(?i)(?<name>Apache)(\s+Software)?(\s+License(s)?(\s*[,-])?)?(\s+V(ersion)?)?\s*(?<version>\d+(\.\d+)?)?" "Apache 2.0")
