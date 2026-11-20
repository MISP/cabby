.PHONY: api html preview

api:
	sphinx-build -q -W -E -b markdown _api _generated

html: api
	quarto render . --to html

preview: api
	quarto preview .
