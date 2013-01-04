from converters.base import Converter
from converters.utils import markdown2rst, rst_directive, remove_ansi
from IPython.utils.text import indent


class ConverterRST(Converter):
    extension = 'rst'
    heading_level = {1: '=', 2: '-', 3: '`', 4: '\'', 5: '.', 6: '~'}

    def render_heading(self, cell):
        marker = self.heading_level[cell.level]
        return ['{0}\n{1}\n'.format(cell.source, marker * len(cell.source))]

    def render_code(self, cell):
        # Note: cell has type 'IPython.nbformat.v3.nbbase.NotebookNode'
        if not cell.input:
            return []

        lines = ['In[%s]:' % self._get_prompt_number(cell), '']
        lines.extend(rst_directive('.. code:: python', cell.input))

        for output in cell.outputs:
            conv_fn = self.dispatch(output.output_type)
            lines.extend(conv_fn(output))

        return lines

    def render_markdown(self, cell):
        #return [cell.source]
        return [markdown2rst(cell.source)]

    def render_raw(self, cell):
        if self.raw_as_verbatim:
            return ['::', '', indent(cell.source), '']
        else:
            return [cell.source]

    def render_pyout(self, output):
        lines = ['Out[%s]:' % self._get_prompt_number(output), '']

        # output is a dictionary like object with type as a key
        if 'latex' in output:
            lines.extend(rst_directive('.. math::', output.latex))

        if 'text' in output:
            lines.extend(rst_directive('.. parsed-literal::', output.text))

        return lines

    def render_pyerr(self, output):
        # Note: a traceback is a *list* of frames.
        return ['::', '', indent(remove_ansi('\n'.join(output.traceback))), '']

    def _img_lines(self, img_file):
        return ['.. image:: %s' % img_file, '']

    def render_display_format_text(self, output):
        return rst_directive('.. parsed-literal::', output.text)

    def _unknown_lines(self, data):
        return rst_directive('.. warning:: Unknown cell') + [data]

    def render_display_format_html(self, output):
        return rst_directive('.. raw:: html', output.html)

    def render_display_format_latex(self, output):
        return rst_directive('.. math::', output.latex)

    def render_display_format_json(self, output):
        return rst_directive('.. raw:: json', output.json)

    def render_display_format_javascript(self, output):
        return rst_directive('.. raw:: javascript', output.javascript)
