"""HTML: PI NodeParser

An HTML processing instruction is enclosed within `<?` and `?>`. It
contains a target and optionally some content. The content is the
node data and it cannot contain the sequence `?>`. A valid processing
instruction is of the form

    <?PITarget*PIContent?>

where `*` is a space character (this includes tabs and new lines).

"""
import re
import traceback
from lexor.core.parser import NodeParser
from lexor.core.elements import (
    ProcessingInstruction, Text, Element, CData
)

RE = re.compile(r'.*?[ \t\n\r\f]')


class ProcessingInstructionNP(NodeParser):
    """Parses content enclosed within `<?PITarget` and `?>`. Note
    that the target of the `ProcessingInstruction` object that it
    returns has `?` prepended to it. """

    # noinspection PyBroadException
    def assemble_node(self, target, content, pos):
        """Create the processing instruction and compile it if the
        target is for python. """
        node = ProcessingInstruction(target, content)
        node.set_position(*pos)
        if target in ['?py', '?python']:
            try:
                node.compile_python(self.parser.uri)
            except BaseException:
                self.msg('E102', pos)
                err_node = Element('python_pi_error')
                err_node.set_position(*pos)
                err_data = CData(traceback.format_exc())
                err_data.set_position(pos[0], pos[1]+1+len(target))
                err_node.append_child(
                    err_data
                )
                return [err_node]
        return node

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
        start = match.end(0) - 1
        if parser.text[start] in [' ', '\t']:
            start += 1
        if index == -1:
            self.msg('E101', pos, [target])
            content = parser.text[start:parser.end]
            parser.update(parser.end)
            return self.assemble_node(target, content, pos)
        content = parser.text[start:index]
        parser.update(index+2)
        return self.assemble_node(target, content, pos)

    def close(self, _):
        pass


MSG = {
    'E100': 'ignoring processing instruction',
    'E101': '`<{0}` was started but `?>` was not found',
    'E102': 'errors in python processing instruction',
}
MSG_EXPLANATION = [
    """
    - A processing instruction must have a target and must be
      enclosed within `<?` and `?>`.

    - If there is no space following the target of the processing
      instruction, that is, if the file ends abruptly, then the
      processing instruction will be ignored.

    Okay: <?php echo '<p>Hello World</p>'; ?>

    E100: <?php
    E101: <?php echo '<p>Hello World</p>';
""", """
    - Python processing instructions must be valid.

    - Invalid code will be replaced with a "python_pi_error" element
      containing the traceback to help you fix the errors.

    Okay: <?py print 'hello world' ?>

    E102: <?py print 'hello world ?>
    E102:
        <?python
        for i in xrange(5)
            print 'hello'
        ?>

"""
]
