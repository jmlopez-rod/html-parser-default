"""HTML: DEFAULT parser ENTITY test

Testing suite to parse html entity in the default style.

"""

from lexor.command.test import nose_msg_explanations


def test_entity():
    """html.parser.default.entity: MSG_EXPLANATION """
    nose_msg_explanations(
        'html', 'parser', 'default', 'entity'
    )
