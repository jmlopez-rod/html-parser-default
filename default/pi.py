"""HTML: PI NodeParser

An HTML processing instruction is enclosed within `<?` and `?>`. It
contains a target and optionally some content. The content is the
node data and it cannot contain the sequence `?>`. A valid processing
instruction is of the form

    <?PITarget*PIContent?>

where `*` is a space character (this includes tabs and new lines).

"""

import re
from lexor.core.parser import NodeParser
from lexor.core.elements import ProcessingInstruction, Text

RE = re.compile('.*?[ \t\n\r\f\v]')


class ProcessingInstructionNP(NodeParser):
    """Parses content enclosed within `<?PITarget` and `?>`. Note
    that the target of the `ProcessingInstruction` object that it
    returns has `?` preappended to it. """

    def make_node(self):
        parser = self.parser
        caret = parser.caret
        if parser.text[caret:caret+2] != '<?':
            return None
        pos = parser.copy_pos()
        match = RE.search(parser.text, caret+1)
        if match:
            target = parser.text[parser.caret+1:match.end(0)-1]
        else:
            self.msg('E100', pos)
            content = parser.text[parser.caret:parser.end]
            parser.update(parser.end)
            return Text(content)
        index = parser.text.find('?>', match.end(0), parser.end)
        if index == -1:
            self.msg('E101', pos, [target])
            content = parser.text[match.end(0):parser.end]
            parser.update(parser.end)
            return ProcessingInstruction(target, content)
        content = parser.text[match.end(0):index]
        parser.update(index+2)
        return ProcessingInstruction(target, content)


MSG = {
    'E100': 'ignoring processing instruction',
    'E101': '`<{0}` was started but `?>` was not found',
}
MSG_EXPLANATION = [
    """
    - A processing instruction must have a target and must be
      enclosed within `<?` and `?>`.

    - If there is no space following the target of the processing
      instruction, that is, if the file ends abrutly, then the
      processing instruction will be ignored.

    Okay: <?php echo '<p>Hello World</p>'; ?>

    E100: <?php
    E101: <?php echo '<p>Hello World</p>';
""",
]
