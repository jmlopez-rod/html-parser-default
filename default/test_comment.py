"""HTML: DEFAULT parser COMMENT test

Testing suite to parse html comment in the default style.

"""

from lexor.command.test import nose_msg_explanations


def test_comment():
    """html.parser.default.comment: MSG_EXPLANATION """
    nose_msg_explanations(
        'html', 'parser', 'default', 'comment'
    )
