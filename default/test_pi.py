"""HTML: DEFAULT parser PI test

Testing suite to parse html pi in the default style.

"""

from lexor.command.test import nose_msg_explanations


def test_pi():
    """html.parser.default.pi: MSG_EXPLANATION """
    nose_msg_explanations(
        'html', 'parser', 'default', 'pi'
    )
