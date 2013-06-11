(ql:quickload :drakma)
(ql:quickload :closure-html)

(defparameter *urls* nil)
(defparameter  *tmp-urls* nil)
(defparameter *no-url* 10)

(push "http://lisp.org" *urls*)

(defun url-from-args (args)
  (if (and args (eq (caar args) :href))
      (cadar args)))

(defun process-lhtml (lhtml)
  (if (and lhtml (listp lhtml))
      (let ((tag (car lhtml))
            (args (cadr lhtml))
            (children (cddr lhtml)))
        (if (eq tag :a)
            (let ((url (url-from-args args)))
              (if (and url (stringp url))
                  (push url *urls*)))
            (mapc #'process-lhtml children)))))

(defun get&parse (url)
  (let ((stream (drakma:http-request url :want-stream t))) ;; :connection-timeout nil ; in case of clisp.
    (chtml:parse stream (chtml:make-lhtml-builder))))

(defun crawl ()
  (loop for i from 1 to *no-url*
     when (not (null *urls*))
     do (let ((url (pop *urls*)))
          (progn
            (format t "~a) Crawling ~a~%" i url)
            (process-lhtml (get&parse url))))))
