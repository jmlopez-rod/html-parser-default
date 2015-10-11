"""HTML: ELEMENT NodeParser

Handles all `Elements` in the form

    <tagname att1="val1" att2="val2">
        ...
    </tagname>

"""

import re
from lexor.core.parser import NodeParser
from lexor.core.elements import Element, Void, RawText


RE = re.compile(r'.*?[ \t\n\r\f\v/>]')
RE_NOSPACE = re.compile(r"\s*")
RE_NEXT = re.compile(r'.*?[ \t\n\r\f\v/>=]')
VOID_ELEMENT = (
    'area', 'base', 'basefont', 'br', 'col', 'frame', 'hr', 'img',
    'input', 'isindex', 'link', 'meta', 'param', 'command', 'embed',
    'keygen', 'source', 'track', 'wbr'
)
RAWTEXT_ELEMENT = (
    'script', 'style', 'textarea', 'title'
)
AUTO_CLOSE = {
    'p': [
        'address', 'article', 'aside', 'blockquote', 'dir', 'div',
        'dl', 'fieldset', 'footer', 'form', 'h1', 'h2', 'h3', 'h4',
        'h5', 'h6', 'header', 'hgroup', 'hr', 'main', 'menu', 'nav',
        'ol', 'p', 'pre', 'section', 'table', 'ul'
    ],
    'a': [
        'a'
    ],
}
AUTO_CLOSE_FIRST = {
    'li': ['li'],
    'dt': ['dt', 'dd'],
    'dd': ['dt', 'dd'],
    'rt': ['rt', 'rp'],
    'rp': ['rt', 'rp'],
    'optgroup': ['optgroup'],
    'option': ['optgroup', 'option'],
    'thead': ['tbody', 'tfoot'],
    'tbody': ['tbody', 'tfoot'],
    'tfoot': ['tbody'],
    'tr': ['tr'],
    'td': ['td', 'th'],
    'th': ['td', 'th'],
}


class ElementNP(NodeParser):
    """Parses all html elements. """

    def is_element(self, parser):
        """Check to see if the parser's caret is positioned in an
        element and return the index where the opening tag ends. """
        caret = parser.caret
        if parser.text[caret:caret+1] != '<':
            return None
        char = parser.text[caret+1:caret+2]
        if char.isalpha() or char in [":", "_"]:
            end_index = parser.text.find('>', caret+1)
            if end_index == -1:
                return None
            start = parser.text.find('<', caret+1)
            if start != -1 and start < end_index:
                self.msg('E100', parser.pos, parser.compute(start))
                return None
        else:
            return None
        return end_index

    def get_raw_text(self, parser, tagname, pos):
        """Return the data content of the RawText object and update
        the caret. """
        index = parser.text.find('<', parser.caret)
        while index != -1:
            tmpstr = parser.text[index:index+len(tagname)+3].lower()
            if tmpstr == '</%s>' % tagname:
                break
            index = parser.text.find('<', index+1)
        if index == -1:
            self.msg('E110', pos, [tagname])
            content = parser.text[parser.caret:]
            parser.update(parser.end)
        else:
            content = parser.text[parser.caret:index]
            parser.update(index+len(tagname)+3)
        return content

    def make_node(self):
        parser = self.parser
        caret = parser.caret
        end_index = self.is_element(parser)
        if end_index is None:
            return None
        pos = parser.copy_pos()
        match = RE.search(parser.text, caret+1)
        tagname = parser.text[parser.caret+1:match.end(0)-1].lower()
        if tagname in VOID_ELEMENT:
            node = Void(tagname)
        elif tagname in RAWTEXT_ELEMENT:
            node = RawText(tagname)
        else:
            node = Element(tagname)
        parser.update(match.end(0)-1)
        if parser.text[parser.caret] is '>':
            parser.update(parser.caret+1)
        elif parser.text[parser.caret] is '/':
            parser.update(end_index+1)
        else:
            self.read_attributes(parser, node, end_index, tagname)
        node.set_position(*pos)
        if isinstance(node, Void):
            return [node]
        if isinstance(node, RawText):
            node.data = self.get_raw_text(parser, tagname, pos)
            return [node]
        node.pos = pos
        return node

    def close(self, node):
        """Return the position where the element was closed. """
        parser = self.parser
        caret = parser.caret
        flag = None
        if parser.text[caret:caret+1] != '<':
            pass
        elif parser.text[caret+1:caret+2] == '/':
            index = parser.text.find('>', caret+2)
            if index == -1:
                return None
            tmptag = parser.text[caret+2:index].lower()
            if node.name == tmptag:
                pos = parser.copy_pos()
                parser.update(index+1)
                return pos
        else:
            flag = self.is_element(parser)
        if flag is None:
            return None
        # http://www.whatwg.org/specs/web-apps/current-work/#optional-tags
        match = RE.search(parser.text, caret+1)
        tmptag = parser.text[parser.caret+1:match.end(0)-1].lower()
        if node.name in AUTO_CLOSE and tmptag in AUTO_CLOSE[node.name]:
            pos = parser.copy_pos()
            return pos
        if node.name in AUTO_CLOSE_FIRST:
            has_element = False
            for child in node.child:
                if isinstance(child, Element):
                    has_element = True
                    break
            if has_element is False and tmptag in AUTO_CLOSE_FIRST[node.name]:
                pos = parser.copy_pos()
                return pos
        return None

    def is_empty(self, parser, index, end, tagname):
        """Checks to see if the parser has reached '/'. """
        if parser.text[index] == '/':
            parser.update(end+1)
            if end - index > 1:
                self.msg('E120', parser.compute(index))
            if tagname not in VOID_ELEMENT:
                self.msg('E121', parser.compute(index))
            return True
        return False

    def read_prop(self, parser, node, end, tagname):
        """Return [prop, prop_index, implied, empty]. """
        prop = None
        prop_index = None
        match = RE_NOSPACE.search(parser.text, parser.caret, end)
        if self.is_empty(parser, match.end(0), end, tagname):
            return prop, prop_index, False, True
        if parser.text[match.end(0)] == '>':
            parser.update(end+1)
            return prop, prop_index, False, False
        prop_index = match.end(0)
        if prop_index - parser.caret == 0 and node.attlen > 0:
            self.msg('E130', parser.pos)
        match = RE_NEXT.search(parser.text, prop_index, end)
        if match is None:
            prop = parser.text[prop_index:end]
            parser.update(end+1)
            return prop, prop_index, True, False
        prop = parser.text[prop_index:match.end(0)-1]
        if self.is_empty(parser, match.end(0)-1, end, tagname):
            return prop, prop_index, True, True
        if parser.text[match.end(0)-1] == '=':
            parser.update(match.end(0))
            return prop, prop_index, False, False
        match = RE_NOSPACE.search(parser.text, match.end(0), end)
        if parser.text[match.end(0)] == '=':
            implied = False
            parser.update(match.end(0)+1)
        else:
            implied = True
            parser.update(match.end(0)-1)
        return prop, prop_index, implied, False

    def read_val(self, parser, end, tagname):
        """Return the attribute value. """
        match = RE_NOSPACE.search(parser.text, parser.caret, end)
        if self.is_empty(parser, match.end(0), end, tagname):
            return ''
        if parser.text[match.end(0)] == '>':
            parser.update(end+1)
            return ''
        val_index = match.end(0)
        if parser.text[val_index] in ["'", '"']:
            quote = parser.text[val_index]
            index = parser.text.find(quote, val_index+1, end)
            if index == -1:
                self.msg('E150', parser.pos, parser.compute(end))
                parser.update(end+1)
                return parser.text[val_index+1:end]
            parser.update(index+1)
            return parser.text[val_index+1:index]
        else:
            pos = parser.copy_pos()
            match = RE.search(parser.text, val_index, end)
            if match is None:
                val = parser.text[val_index:end]
                for item in '\'"=':
                    if item in val:
                        self.msg('E140', pos, [item])
                parser.update(end+1)
                return val
            if parser.text[match.end(0)-1] == '/':
                self.msg('E141', pos)
                parser.update(match.end(0)-1)
            else:
                parser.update(match.end(0)-1)
            val = parser.text[val_index:match.end(0)-1]
            for item in '\'"=':
                if item in val:
                    self.msg('E140', pos, [item])
            return val

    def read_attributes(self, parser, node, end, tname):
        """Parses the string

            parser.text[parser.caret:end]

        and writes the information in node.

            att1="val1" att2="val2" ...

        This function returns True if the opening tag ends with `/`. """
        while parser.caret < end:
            prop, prop_index, implied, empty = self.read_prop(
                parser, node, end, tname
            )
            if prop is None:
                return empty
            if prop in node:
                self.msg('E160', parser.compute(prop_index), [prop])
            if implied is True:
                node[prop] = ""
                if empty is True:
                    return empty
            else:
                val = self.read_val(parser, end, tname)
                node[prop] = val
        parser.update(end+1)


MSG = {
    'E100': 'element discarted due to `<` at {0}:{1:2}',
    'E110': '`RawText` closing tag `</{0}>` not found',
    'E120': '`/` not immediately followed by `>`',
    'E121': 'self-closing syntax (`/>`) used in non-void element',
    'E130': 'no space between attributes',
    'E140': '`{0}` found in unquoted attribute value',
    'E141': '`/` found in unquoted attribute value',
    'E150': 'assuming quoted attribute to close at {0}:{1:2}',
    'E160': 'attribute name "{0}" has already been declared',
}
MSG_EXPLANATION = [
    """
    - The opening tag of an element cannot contain `<`. This means
      that attributes cannot contain `<` in them.

    Okay: <apple att1="val1"></apple>

    E100: <apple att1="a < b"></apple>
""",
    """
    - `RawText` elements are terminated when the appropiate closing
      tag is found. Make sure to provide its proper closing tag.

    Okay: <title>My awesome website</title>
    Okay: <script>a < b && b > c</script>

    E110: <title>My sheetie website</title >
    E110: <title>My sheetie website< / title >
    E110: <title>My sheetie website
    E110: <script>a < b && b > c
""",
    """
    - A `Void` Element's opening tag must end with `/>`. Anything in
      between the characters `/` and `>` will be ignored.

    - Non-void elements whose opening tag start with `/>` will be
      also be interpreted correctly a message will be issued.

    Okay: <img href="/path/to/image.png"/>
    Okay: <p>starting a new paragraph</p>

    E120: <img href="/path/to/image.png"/  >
    E121: <p />starting a new paragraph</p>
""",
    """
    - Attributes need to be separated by one space.

    - Do not repeat attributes since the values will only get
      overwritten.

    Okay: <tag att1="val1" att2="val2">content</tag>
    Okay: <tag att1='1' att2='2'></tag>

    E130: <tag att1="val1"att2="val2">content</tag>
    E160: <tag att1='1' att1='2'></tag>
""",
    """
    A few attributes rules:

    - There is a risk of joining attributes together when using
      unquoted attribute values. This may result in having a quote or
      equal sign inside the unquoted attribute value. [E140]

    - If your attribute contains `/` then the attribute should be
      quoted. [E141]

    - Quoted attributes need to be finished by its starting quotation
      character. [E150]

    Okay: <tag att1=val1 att2="val2">content</tag>
    E140: <tag att1=val1att2="val2">content</tag>

    Okay: <img href="path/to/image.png" />
    E141: <img href=path/to/image.png />

    Okay: <tag att1="num"></tag>
    Okay: <tag att1='num'></tag>

    E150: <tag att1="num></tag>
    E150: <tag att1='num></tag>
""",
]
