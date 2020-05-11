import re

from pygments import token as T
from pygments.filter import simplefilter


@simplefilter
def text_to_whitespace_token(self, lexer, stream, options):
    """ Converts a Blank Text Token to Whitespace Token.

    Arguments:
        See Pygments documentation for User Filters 
        using simplefilter decorator.

    Yields:
        See Pygments documentation for User Filters 
        using simplefilter decorator.
    """
    for ttype, value in stream:
        if ttype is T.Text and value.strip() == '':
            ttype = T.Whitespace
            value = ' '
        yield ttype, value


@simplefilter
def float_to_punctuation_token(self, lexer, stream, options):
    """ Converts a Float Token having value '.' to Punctuation Token.

    Arguments:
        See Pygments documentation for User Filters 
        using simplefilter decorator.

    Yields:
        See Pygments documentation for User Filters 
        using simplefilter decorator.
    """
    for ttype, value in stream:
        if ttype is T.Number.Float and value == '.':
            ttype = T.Punctuation
        yield ttype, value


@simplefilter
def float_to_integer_token(self, lexer, stream, options):
    """ Converts a Float Token having value '.' to Integer Token.

    Arguments:
        See Pygments documentation for User Filters 
        using simplefilter decorator.

    Yields:
        See Pygments documentation for User Filters 
        using simplefilter decorator.
    """
    for ttype, value in stream:
        if ttype is T.Number.Float and re.match("^\d+$", value.strip(), re.ASCII):
            ttype = T.Number.Integer
        yield ttype, value
