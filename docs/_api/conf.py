"""Convert Cabby's Python docstrings to Markdown for the Quarto API chapter."""

project = 'Cabby'
root_doc = 'api'
extensions = ['sphinx.ext.autodoc', 'myst_parser', 'sphinx_markdown_builder']
source_suffix = {'.md': 'markdown'}
markdown_anchor_sections = True
markdown_anchor_signatures = True


def setup(app):
    from docutils import nodes

    def expand_abbreviations(app, doctree, docname):
        # Preserve the keyword-only (*) and positional-only (/) markers in signatures.
        for node in doctree.findall(nodes.abbreviation):
            node.replace_self(nodes.Text(node.astext()))

    app.connect('doctree-resolved', expand_abbreviations)
