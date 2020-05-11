''' Defines the Token and Statement class used for SQL parsing.
    Parts of the code are similar to / copied from sqlparse: https://github.com/andialbrecht/sqlparse
'''

from pygments.token import Comment, Whitespace

import sqlsense.tokens as ST


class Token(object):
    ''' Token class
    '''

    def __init__(self, ttype, value):
        self._ttype = ttype
        self._value = value
        self._parent = None

    def __str__(self):
        return self.value()

    def __repr__(self):
        return "[{0}:{1}:{2}]".format(self.__class__.__name__, str(self.ttype).split('.')[-1], self.value())

    @property
    def ttype(self):
        return self._ttype

    @ttype.setter
    def ttype(self, value):
        self._ttype = value

    @property
    def parent(self):
        return self._parent

    def value(self, suppress_comment=False):
        ''' Implement the function in Child class as per requirement
        '''
        if not (suppress_comment and self._ttype in Comment):
            return self._value
        else:
            return ''

    def match_type_value(self, other):
        return (self._ttype == other.ttype and self.value() == other.value()) if (type(other) == type(self)) else False

    def flatten(self, suppress_whitespace=False, suppress_comment=False):
        if not((suppress_comment and self._ttype in Comment) or (suppress_whitespace and self._ttype in Whitespace)):
            yield self


class TokenGroup(Token):
    ''' Token Group class
    '''

    def __init__(self, token_list=None, ttype=None):
        self._token_list = token_list or []
        # for all token in token list, set myself as the parent
        [setattr(token, '_parent', self) for token in self._token_list]
        super().__init__(ttype, None)

    @property
    def token_list(self):
        return self._token_list

    @property
    def token_count(self):
        return len(self._token_list)

    def value(self, suppress_comment=False):
        return ''.join(token.value(suppress_comment) for token in self._token_list)

    def flatten(self, suppress_whitespace=False, suppress_comment=False):
        ''' Generator yielding ungrouped tokens.
            This method is recursively called for all child tokens.
        '''
        for token in self._token_list:
            for item in token.flatten(suppress_whitespace, suppress_comment):
                yield item

    def get_identifiers(self):
        """ Generates Identifiers in the SQL Statement.
        """
        for token in self._token_list:
            if (token._ttype in (ST.Identifier, ST.Function, ST.SubQuery) or
                    (token._ttype in (ST.ComputedIdentifier, ST.SelectConstantIdentifier) and token.parent._ttype == ST.SelectClause)):
                yield token
            if isinstance(token, TokenGroup):
                for item in token.get_identifiers():
                    yield item

    def append(self, token):
        ''' Appends the supplied token to the token list and 
            set self as its parent.
        '''
        if isinstance(token, Token) or isinstance(token, TokenGroup):
            token._parent = self
            self._token_list.append(token)

    def insert(self, index, token):
        ''' Inserts the supplied token to the token list at the given index position and 
            set self as its parent.
        '''
        if isinstance(token, Token) or isinstance(token, TokenGroup):
            token._parent = self
            self._token_list.insert(index, token)

    def pop_whitespace_token(self):
        ''' Pop the last token if it is a Whitespace and return True
            else return False
        '''
        if self._token_list[-1].match_type_value(Token(Whitespace, ' ')):
            self._token_list = self._token_list[:-1]
            return True
        else:
            return False

    def has_token_as_immediate_child(self, check_token):
        ''' Checks if the supplied token exists in the token_list.
            The check is not performed recursively for sub TokenGroups.
        '''
        for token in self._token_list:
            if token.match_type_value(check_token):
                return True
        return False

    def token_before(self, next_token_index=None, suppress_whitespace=True, suppress_comment=True):
        token_list_index = next_token_index if (
            next_token_index and next_token_index < self.token_count) else self.token_count
        while token_list_index > 0:
            token_list_index = token_list_index - 1
            if not ((suppress_whitespace and self._token_list[token_list_index]._ttype == Whitespace) or
                    (suppress_comment and self._token_list[token_list_index]._ttype == Comment)):
                return self._token_list[token_list_index]

    def token_index_before(self, next_token_index=None, suppress_whitespace=True, suppress_comment=True):
        token_list_index = next_token_index if (
            next_token_index and next_token_index < self.token_count) else self.token_count
        while token_list_index > 0:
            token_list_index = token_list_index - 1
            if not ((suppress_whitespace and self._token_list[token_list_index]._ttype == Whitespace) or
                    (suppress_comment and self._token_list[token_list_index]._ttype == Comment)):
                return token_list_index

    def last_token(self, suppress_whitespace=True, suppress_comment=True):
        return self.token_before(suppress_whitespace=suppress_whitespace, suppress_comment=suppress_comment)

    def last_token_index(self, suppress_whitespace=True, suppress_comment=True):
        return self.token_index_before(suppress_whitespace=suppress_whitespace, suppress_comment=suppress_comment)

    def merge_into_token_group(self, ttype, token_list_start_index_included=0, token_list_end_index_excluded=None):
        """ Merge a given subset of tokens within a token group into a new token group.

        Arguments:
            ttype {TokenType} -- [Token Type of the new Group]

        Keyword Arguments:
            token_list_start_index_included {int} -- [Start Index of the subset (included)] (default: {0})
            token_list_end_index_excluded {[type]} -- [End Index of the subset (excluded)] (default: {None})

        Returns:
            [TokenGroup] -- [New Token Group formed by merging the subset of tokens]
        """
        if token_list_end_index_excluded is None:
            token_list_end_index_excluded = self.token_count
        items_to_remove = token_list_end_index_excluded - token_list_start_index_included
        new_grp = TokenGroup(ttype=ttype)
        for i in range(items_to_remove):
            new_grp.append(self._token_list.pop(
                token_list_start_index_included))
        self.insert(token_list_start_index_included, new_grp)
        return new_grp


class SqlStatement(TokenGroup):
    ''' SQL Statement class
    '''

    def __init__(self, token_list=None, ttype=None):
        super().__init__(token_list=token_list, ttype=ttype)

    def datasets_involved(self):
        return NotImplementedError
