(ns clj.core
  (:require [hickory.core :as hickory]
            [hickory.select :as s]
            [clj-http.client :as client]
            [clojure.tools.cli :refer [parse-opts]])
  (:import [java.net URL MalformedURLException]))

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

(defn get-all-links [url]
  (let [base-url (URL. url)
        htree (-> (client/get url) :body hickory/parse hickory/as-hickory)]
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

(defn uncrawled-url [crawled urls]
  (loop [url (first urls)
         urls-to-consider (rest urls)]
    (if (not (contains? crawled url))
      url
      (recur (first urls-to-consider)
             (rest urls-to-consider)))))

(defn crawl [url max-urls]
  (loop [urls #{url}
         crawled #{}
         count 0]
    (if (>= count max-urls)
      crawled
      (let [url-to-crawl (uncrawled-url crawled urls)]
        (println (str "Url beeing crawled " url-to-crawl))
        (recur (into urls (try
                            (get-all-links url-to-crawl)
                            (catch Exception e #{})))
               (conj crawled url-to-crawl)
               (inc count))))))

(defn -main [& args]
  (let [options (parse-opts args cli-options)]
    (if ((options :options) :help)
      (println (str "Ex: lein run\n"
                    (options :summary)))
      (println (str ((options :options) :max-urls)
                    (crawl ((options :options) :initial-url)
                           ((options :options) :max-urls)))))))
