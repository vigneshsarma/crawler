(ns clj.core
  (:refer-clojure :exclude [map reduce into partition partition-by take merge])
  (:require [hickory.core :as hickory]
            [hickory.select :as s]
            [clj-http.client :as client]
            [clojure.tools.cli :refer [parse-opts]]
            [clojure.core.async :refer :all :as async ])
  (:import [java.net URL MalformedURLException]))

(def concurrency 6)

(def urls-to-crawl (chan (* concurrency 3)))

(def crawl-result (chan (* concurrency 3)))

(def cli-options
  [["-u" "--initial-url" "Initial url/ seed url"
    :default "http://google.co.in"] ;;"http://en.wikipedia.org/"
   ["-m" "--max-urls" "maximum number of urls to crawl."
    :default 50
    :parse-fn #(Integer/parseInt %)]
   ["-h" "--help"]])

(defn relative->full-url [base-url possible-relative]
  (try
    (str (URL. base-url possible-relative))
    (catch MalformedURLException e base-url)))

(defn crawlable? [url]
  (cond (not (nil? (re-find #"^http" url)))
        true
        :else
        true))

(defn get-all-links [url response]
  (let [base-url (URL. url)
        htree (-> response :body hickory/parse hickory/as-hickory)]
    (loop [elms (-> (s/select (s/child
                   (s/attr :href))
                  htree))
           urls #{}]
      (cond (empty? elms)
            urls
            (crawlable? (:href (:attrs (first elms))))
            (recur (rest elms)
                   (conj urls (relative->full-url base-url
                                                  (:href (:attrs (first elms))))))
            :else
            (recur (rest elms) urls)))))

(defn uncrawled-url [exclude urls]
  (loop [url (first urls)
         urls-to-consider (rest urls)]
    (if (not (contains? exclude url))
      url
      (recur (first urls-to-consider)
             (rest urls-to-consider)))))


(defn fetch-url [no]
  (go-loop []
    (when-let [url (<! urls-to-crawl)]
      (try
        (let [resp (client/get url)]
        ;; (println (str "Go  " no " : " (resp :status)))
          (>! crawl-result {:url url
                            :response resp}))
        (catch Exception e
          (println (str "Error: fetch " url " faild.")))))
    (recur)))

(defn crawl-init [seed-url]
  (loop [no 0]
    (if (< no concurrency)
      (do
        (fetch-url no)
        (recur (inc no)))))
  (>!! urls-to-crawl seed-url))

(defn crawl [seed-url max-urls]
  (crawl-init seed-url)
  (loop [urls #{}
         in-process #{seed-url}
         crawled #{}
         count-urls 0]
    (cond (>= count-urls max-urls)
          (do
            (close! urls-to-crawl)
            crawled)
          (or (= (count urls) 0) (>= (count in-process)
                                     (* concurrency 2)))
          (let [{:keys [url response]} (<!! crawl-result)]
            (println (str "Url crawled " url))
            (recur (clojure.core/into urls (get-all-links url response))
                   (disj in-process url)
                   (conj crawled url)
                   (inc count-urls)))
          :else
          (let [url (uncrawled-url
                     (clojure.core/into crawled in-process) urls)]
            (>!! urls-to-crawl url)
            (recur urls (conj in-process url) crawled count-urls)))))

(defn -main [& args]
  (let [{:keys [options summary]} (parse-opts args cli-options)]
    (if (options :help)
      (println (str "Ex: lein run\n"
                    summary))
      (println (str (options :max-urls)
                    (crawl (options :initial-url)
                           (options :max-urls)))))))
