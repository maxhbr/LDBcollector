# SPDX-License-Identifier: MIT

licenses.json: ../pull.py
	$<

commit: licenses.json
	git add -A .
	git commit -m "$$(git -C .. log -1 --format='Rebuild with %h (%s)')"
