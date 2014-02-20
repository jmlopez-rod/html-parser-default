"""HTML: DEFAULT parser CDATA test

Testing suite to parse html cdata in the default style.

"""

from lexor.command.test import nose_msg_explanations


def test_cdata():
    """html.parser.default.cdata: MSG_EXPLANATION """
    nose_msg_explanations(
        'html', 'parser', 'default', 'cdata'
    )
