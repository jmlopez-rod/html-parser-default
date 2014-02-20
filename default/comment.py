"""HTML: COMMENT NodeParser

An HTML comment is enclosed within `<!--` and `-->`. The string `--`
(double-hyphen) MUST NOT occur within comments. If the string starts
with `<!` then it is still a comment but a warning will be issued.

See: <http://www.w3.org/TR/REC-xml/#sec-comments>

"""

from lexor.core.parser import NodeParser
from lexor.core.writer import replace
from lexor.core.elements import Comment


class CommentNP(NodeParser):
    """Creates `Comment` nodes from comments written in HTML. """

    def _handle_bogus(self, parser, caret):
        """Helper method for make_node. """
        self.msg('E100', parser.pos)
        index = parser.text.find('>', caret+2)
        if index == -1:
            parser.update(parser.end)
            self.msg('E201', parser.pos)
            content = parser.text[caret+2:parser.end]
            return Comment(replace(content, ('--', '- ')))
        pos = parser.compute(index)
        self.msg('E300', pos)
        parser.update(index+1)
        content = replace(parser.text[caret+2:index], ('--', '- '))
        return Comment(content)

    def make_node(self):
        parser = self.parser
        caret = parser.caret
        if parser.text[caret:caret+2] != '<!':
            return None
        if parser.text[caret+2:caret+4] != '--':
            return self._handle_bogus(parser, caret)
        index = parser.text.find('--', caret+4)
        if index == -1:
            self.msg('E200', parser.pos)
            parser.update(parser.end)
            return Comment(parser.text[caret+4:parser.end])
        content = parser.text[caret+4:index]
        while parser.text[index:index+3] != '-->':
            self.msg('E301', parser.compute(index), tuple(parser.pos))
            content += '- '
            newindex = parser.text.find('--', index+1)
            if newindex == -1:
                content += parser.text[index+2:parser.end]
                self.msg('E200', parser.pos)
                parser.update(parser.end)
                return Comment(content)
            content += parser.text[index+2:newindex]
            index = newindex
        parser.update(index+3)
        return Comment(content)


MSG = {
    'E100': 'bogus comment started',
    'E200': '`-->` not found',
    'E201': '`>` not found',
    'E300': '`>` found',
    'E301': '`--` in comment opened at {0}:{1:2}',
}
MSG_EXPLANATION = [
    """
    - Bogus comments are detected when the parser reads `<!` and
      the next sequence of characters is not `--`.

    - Always start comments with `<!--`.

    Okay: <!--simple comment-->

    E100: <!simple comment-->
    E100: <!-simple comment-->
    E100: <!- -simple comment-->
""",
    """
    - Comments end with the character sequence `-->`.

    - The parser will assume that the termination of the comment is
      at the end of the file.

    Okay: <!--x -> y-->

    E200: <!--x -> y
    E200: <!--x -> y-- >
    E200: <!--x -> y ->
""",
    """
    - When a bogus comment is started, the parser is forced to look
      for the character `>` as its termination sequence instead of
      `-->`.

    - The original message informs you if `>` was found or not.

    Okay: <!-- comment -->
    E300: <! comment >
    E201: <! comment
""",
    """
    - The character sequence `--` must not appear within a comment.

    - This sequence will be interpreted as `- `.

    Okay: <!-- 1 - 2 - 3 - 4 - 5 -->
    E301: <!-- 1 -- 2 -- 3 -- 4 -- 5 -->
""",
]
