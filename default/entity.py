"""HTML: ENTITY NodeParser

Some characters are reserved in HTML: `<` and `&`. To be able
to display them we need to use HTML entities. The parser defined
in this module looks for such entities.

"""

import re
from lexor.core.parser import NodeParser
from lexor.core.elements import Entity, Text

RE = re.compile('.*?[ \t\n\r\f\v;]')


class EntityNP(NodeParser):
    """Processes `<` and `&` characters. This parser needs to be
    called only after all the other parsers have attempted to decide
    what to do with `<` and `&`."""

    def _handle_lt(self, parser, caret):
        """Helper function for make_node. """
        if parser.text[caret+1:caret+2] == '/':
            tmp = parser.text.find('>', caret+2)
            if tmp == -1:
                self.msg('E100', parser.pos, ['<'])
                parser.update(caret+1)
                return Entity('&lt;')
            else:
                stray_endtag = parser.text[caret:tmp+1]
                self.msg('E101', parser.pos, [stray_endtag])
                parser.update(tmp+1)
                return Text('')
        else:
            self.msg('E100', parser.pos, ['<'])
            parser.update(caret+1)
            return Entity('&lt;')

    def _handle_amp(self, parser, caret):
        """Helper function for make_node. """
        match = RE.search(parser.text, caret)
        if not match:
            self.msg('E100', parser.pos, ['&'])
            parser.update(caret+1)
            return Entity('&amp;')
        if parser.text[match.end()-1] != ';':
            self.msg('E100', parser.pos, ['&'])
            parser.update(caret+1)
            return Entity('&amp;')
        parser.update(match.end())
        return Entity(parser.text[caret:match.end()])

    def make_node(self):
        parser = self.parser
        caret = parser.caret
        if parser.text[caret] == '<':
            return self._handle_lt(parser, caret)
        if parser.text[caret] == '&':
            return self._handle_amp(parser, caret)
        return None


MSG = {
    'E100': 'stray `{0}` found',
    'E101': 'ignoring stray end tag `{0}`',
}
MSG_EXPLANATION = [
    """
    - HTML has `<` and `&` as reserved characters. To be able to
      display `<` you must write the entity `&lt;` or `&#60;`. To
      write `&` you can use the entity `&amp;`

    Okay: a &lt; b
    Okay: I like M&amp;Ms

    E100: a < b
    E100: I like M&Ms
""",
    """
    - Stray end tags are usually an indication of an error. The short
      message tells you the location of the stray end tag but there
      is nothing that can be said about the possible error.

    Okay: <apples><bananas></bananas></apples>
    E101: <apples></bananas></apples>
""",
]
