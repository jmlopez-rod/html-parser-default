Lexor Language: HTML default style parser
=========================================

This style attempts to follow all the HTML rules. It captures all the
information in the file. This includes all the extra spaces, new
lines and tab characters the file might contain.

## Installation

For a local installation 

    $ lexor install html.parser.default

If there is a problem with the registry you may try a more direct
approach

    $ lexor install git+https://github.com/jmlopez-rod/html-parser-default

You may use the `-u` option to install in the python user-site
directory or `-g` for a global installation (requires sudo rights).

If you have a `lexor.config` file in place you may also want to use
the `--save` option so that the dependency gets saved.

## Command line usage

Without document conversion

    $ lexor filename.html to language~writing_style~

Converting to another language and writing it with this style

    $ lexor filename.html to language[converting_style:other_language.writing_style]

You may use this parser even if the file extension is not `html`

    $ lexor filename.ext to <language_options> --from html:default

## Example

For this example we require the following writing styles:

- <https://github.com/jmlopez-rod/lexor-writer-repr>
- <https://github.com/jmlopez-rod/html-writer-default>

Suppose we have the html file `example.html` with the following
content

```html
<html>
<body>
<?py
for i in xrange(3):
    print 'hello world'
?>
</body>
</html>
```

We can check if the html file is valid by running the parser through
it and writing its representation using the lexor repr writing style.

```console
$ lexor example.html to lexor~repr~
#document: (example.html:html:default)
html:
  #text: '\n'
  body:
    #text: '\n'
    ?py: "\nfor i in xrange(3):\n    print 'hello world'\n"
    #text: '\n'
  #text: '\n'
#text: '\n'
```

Lets assume now that we remove the colon in the python code

```console
$ lexor example.html to lexor~repr~
example.html:3: 1: [E102] errors in python processing instruction
#document: (example.html:html:default)
html:
  #text: '\n'
  body:
    #text: '\n'
    python_pi_error:
      #cdata-section:
        |Traceback (most recent call last):
        |  File "/Users/jmlopez-rod/Github/lexor-lang-repos/html-parser-default/default/pi.py", line 36, in assemble_node
        |    node.compile_python(self.parser.uri)
        |  File "/Users/jmlopez-rod/Github/lexor/lexor/core/elements.py", line 121, in compile_python
        |    self._code = compile(data, uri, 'exec')
        |  File "example.html", line 4
        |    for i in xrange(3)
        |                     ^
        |SyntaxError: invalid syntax
        |
    #text: '\n'
  #text: '\n'
#text: '\n'
```

This on its own already tells you the exact line where we can fix
the error.

If you wish to get a modified version of your html file you can run
it through the html default writer.

```console
lexor example.html to html~_~
<html>
<body><?py
for i in xrange(3):
    print 'hello world'
?>
</body>
</html>
```

Note that `_` is equivalent to `default` when using the command line.
