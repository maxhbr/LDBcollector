;;;; lice_comb.impl.3rd_party.clj
;;;
;;; Code obtained from third party sources, but not available via standard
;;; package-consumption mechanisms (i.e. as Maven artifacts)
;;;
;;; Copyright and license information is on a per-code-snippet basis, and
;;; is communicated inline via further comments.
;;;
(ns lice-comb.impl.3rd-party)

;; rdrop-while is copyright © Joshua Suskalo (https://github.com/IGJoshua) 2023 and licensed as "CC0-1.0 OR MIT"
;;
;; Source: https://discord.com/channels/729136623421227082/732641743723298877/1141786961875583097
;; Link to request access: https://discord.gg/discljord
;;
;; Note that the lice-comb project elects to consume this code under the MIT license
(defn rdrop-while
  "As for clojure.core/drop-while, but drops from the end of the
  sequence backwards, rather than the front forwards. More efficient
  when provided with a vector rather than a list."
  ([pred coll]
   (if (reversible? coll)
     (take (- (count coll) (count (take-while pred (rseq coll)))) coll)
     (reverse (drop-while pred (reverse coll)))))
  ([pred]
   (fn [rf]
     (let [stash (volatile! [])]
       (fn
         ([] (rf))
         ([acc] (rf acc))
         ([acc elt]
          (if (pred elt)
            (do (vswap! stash conj elt)
                acc)
            (let [res (reduce rf acc (conj @stash elt))]
              (vreset! stash [])
              res))))))))
