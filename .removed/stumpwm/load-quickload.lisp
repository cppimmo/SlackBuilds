(format t (concatenate 'string "~1%You need to run a few commands now in the"
					   " following order:~%(quicklisp-quickstart:install)~%(ql"
					   ":add-to-init-file)~%(ql:quickload \"clx\")~%(ql:quickl"
					   "oad \"cl-ppcre\")~%(ql:quickload \"alexandria\")~2%"))
(load "quicklisp.lisp")
