"""
HTML parser: default
====================

This parser style attempts to follow all the HTML rules. It captures
all the information in the file. This includes all the extra spaces,
new lines and tab characters the file might contain.

"""
from lexor import init, load_aux

INFO = init(
    version=(0, 0, 1, 'beta', 4),
    lang='html',
    type='parser',
    description='parses html files',
    git={
        'host': 'github',
        'user': 'jmlopez-rod',
        'repo': 'html-parser-default'
    },
    author={
        'name': 'Manuel Lopez',
        'email': 'jmlopez.rod@gmail.com'
    },
    docs='http://jmlopez-rod.github.io/'
         'lexor-lang/html-parser-default',
    license='BSD License',
    path=__file__
)
MOD = load_aux(INFO)
MAPPING = {
    '__default__': (
        '<&', [
            MOD['element'].ElementNP,
            MOD['cdata'].CDataNP,
            MOD['doctype'].DocumentTypeNP,
            MOD['comment'].CommentNP,
            MOD['pi'].ProcessingInstructionNP,
            MOD['entity'].EntityNP,
        ]),
}
