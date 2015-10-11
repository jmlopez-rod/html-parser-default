"""HTML: DEFAULT parser CDATA test

Testing suite to parse html cdata in the default style.

"""
import lexor
from lexor.command.test import nose_msg_explanations, eq_

HTML_SETTINGS = {
    'parser_lang': 'html',
    'convert': 'false'
}


def test_cdata():
    """html.parser.default.cdata: MSG_EXPLANATION """
    nose_msg_explanations(
        'html', 'parser', 'default', 'cdata'
    )


def test_node_position():
    """html.parser.default.cdata: node_position """
    txt_test = """\ntxt<![CDATA[We can write a < b and M&Ms.]]>txt"""
    doc_test, _ = lexor.lexor(txt_test, **HTML_SETTINGS)
    eq_(doc_test[1].node_position, (2, 4))
