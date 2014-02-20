"""HTML: DEFAULT parser DOCTYPE test

Testing suite to parse html doctype in the default style.

"""

from lexor.command.test import nose_msg_explanations


def test_doctype():
    """html.parser.default.doctype: MSG_EXPLANATION """
    nose_msg_explanations(
        'html', 'parser', 'default', 'doctype'
    )
