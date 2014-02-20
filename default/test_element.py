"""HTML: DEFAULT parser ELEMENT test

Testing suite to parse html element in the default style.

"""

from lexor.command.test import nose_msg_explanations


def test_element():
    """html.parser.default.element: MSG_EXPLANATION """
    nose_msg_explanations(
        'html', 'parser', 'default', 'element'
    )
