"""HTML: DOCTYPE NodeParser

DOCTYPE is case insensitive in HTML. The following forms are valid:

    <!doctype html>
    <!DOCTYPE html>
    <!DOCTYPE HTML>
    <!DoCtYpE hTmL>

See: <http://stackoverflow.com/a/9109157/788553>

"""
from lexor.core.parser import NodeParser
from lexor.core.elements import DocumentType


class DocumentTypeNP(NodeParser):
    """Obtains the content enclosed within `<!doctype` and `>`. """

    def make_node(self):
        parser = self.parser
        caret = parser.caret
        if parser.text[caret:caret+9].lower() != '<!doctype':
            return None
        pos = parser.copy_pos()
        char = parser.text[caret+9:caret+10]
        if char not in ' \t\n\r\f\v':
            return None
        index = parser.text.find('>', caret+10)
        if index == -1:
            self.msg('E100', parser.pos)
            parser.update(parser.end)
            content = parser.text[caret+10:parser.end]
            return DocumentType(content).set_position(*pos)
        parser.update(index+1)
        content = parser.text[caret+10:index]
        return DocumentType(content).set_position(*pos)

    def close(self, _):
        pass

MSG = {
    'E100': '`>` not found',
}
MSG_EXPLANATION = [
    """
    - A `doctype` element starts with `<!doctype` and it is
      terminated by `>`.

    Okay: <!doctype html>
    Okay: <!DOCTYPE html>

    E100: <!doctype html
""",
]
