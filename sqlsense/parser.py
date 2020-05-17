from pygments import token as T
from pygments.lexers.sql import SqlLexer

import sqlsense.tokens as ST
from sqlsense.filter import text_to_whitespace_token
from sqlsense.sql import SqlStatement, Token, TokenGroup


class SqlParser(object):
    """ Base class for all SQL Parsers. Not to be used for actual parsing.
    """

    def __init__(self, lexer_object=SqlLexer, end_marker_token=Token(T.Punctuation, ';')):
        self._lexer = lexer_object(stripall=True)
        # self._lexer.add_filter('keywordcase', case='upper')
        self._lexer.add_filter(text_to_whitespace_token())
        self._end_marker_token = end_marker_token
        self._parse_rules = self._set_rules_()

    def _get_sql_statement(self):
        """ Returns the SQL Statement class instance
            Child Class may override this function to return 
            an improved/extended SQL Statement
        Returns:
            [class object instance] -- SqlStatement class instance
        """
        return SqlStatement()

    def parse(self, sql_text):
        def token_stream(sql_text):
            for ttype, value in self._lexer.get_tokens(sql_text):
                yield Token(ttype, value)

        stmt = self._get_sql_statement()
        curr_tk_grp = stmt
        for tk in token_stream(sql_text):
            # print('{0}: <{1}>'.format(tk.ttype, tk.value()))
            if tk.match_type_value(self._end_marker_token):
                # Statement complete
                stmt.append(tk)
                yield stmt
                stmt = self._get_sql_statement()
                curr_tk_grp = stmt
                continue
            rule_key = str(tk.ttype)
            if tk.ttype == T.Keyword:
                rule_key = 'Token.Keyword.{0}'.format(tk.value().upper())
            elif tk.ttype in T.Number:
                rule_key = 'Token.Literal.Number'
            elif tk.ttype in T.String:
                rule_key = 'Token.Literal.String'
            else:
                rule_key = str(tk.ttype)
            action = self._parse_rules[rule_key] if rule_key in self._parse_rules else None
            if action:
                curr_tk_grp = action(stmt, curr_tk_grp, tk)
            else:
                curr_tk_grp.append(tk)

        while curr_tk_grp != stmt:
            curr_tk_grp = self._switch_to_parent(curr_tk_grp)
        if stmt.ttype is not None and len(stmt.value().strip()) > 0:
            yield stmt
        return 0

    def _switch_to_parent(self, token_group):
        if token_group.pop_whitespace_token():
            # If Token Group has Whitespace at its end, move ito its Parent Group
            token_group.parent.append(Token(T.Whitespace, ' '))
        return token_group.parent

    def _setup_computed_identifier(self, stmt, token_group, token):
        if token.value() in ('+', '-', '*', '/', '%', '^'):
            if token_group.ttype == ST.SelectConstantIdentifier:
                token_group.ttype = ST.ComputedIdentifier
            while token_group.ttype not in (ST.ComputedIdentifier, ST.SelectClause, ST.JoinOnClause,
                                            ST.WhereClause, ST.GroupByClause, ST.HavingClause, ST.OrderByClause,
                                            ST.RoundBracket, ST.ConditionGroup, ST.CollectionSet,
                                            ST.Comparison, ST.Between, ST.Like,
                                            ST.Not, ST.NotBetween, ST.NotLike,
                                            ST.CaseExpression, ST.WhenExpression, ST.ThenExpression, ST.ElseExpression):
                token_group = self._switch_to_parent(token_group)
            if token_group.ttype != ST.ComputedIdentifier:
                token_group = token_group.merge_into_token_group(
                    ST.ComputedIdentifier, token_list_start_index_included=token_group.last_token_index())
        token_group.append(token)
        return token_group

    def _process_select_clause(self, stmt, token_group, token):
        select_clause_grp = TokenGroup([token, ], ST.SelectClause)
        if token_group.ttype is not None and token_group.ttype not in (ST.InsertIntoClause, ST.RoundBracket, ST.CollectionSet):
            # If Select Clause is preceeded by Insert Into Clause, get out of that Clause Token Group
            token_group = self._switch_to_parent(token_group)

        token_group.append(select_clause_grp)

        # If we are at the Statement Token Group, set the Statement Type
        if token_group == stmt:
            if token_group.ttype is None:
                token_group.ttype = ST.Select
            elif token_group.ttype is ST.Insert:
                token_group.ttype = ST.InsertIntoSelect
        elif token_group.ttype in (ST.RoundBracket, ST.CollectionSet):
            # TODO: Should we check the preceeding token to make sure SELECT is the first keyword in Brackets
            token_group.ttype = ST.SubQuery
        return select_clause_grp

    def _process_from_clause(self, stmt, token_group, token):
        from_clause_grp = TokenGroup([token, ], ST.FromClause)

        while token_group.ttype not in (ST.SelectClause, ST.SelectIntoClause, ST.UpdateSetClause):
            # TODO: Think about Delete From Clause before getting out
            # Get out of the Token Group until you find preceeding
            # (Select Clause, Select Into Clause, Update Set Clause)
            token_group = self._switch_to_parent(token_group)

        # Get out of the Clause Token Group and exit
        token_group = self._switch_to_parent(token_group)
        token_group.append(from_clause_grp)
        # TODO: Think about Delete From Clause before returning
        return from_clause_grp

    def _process_where_clause(self, stmt, token_group, token):
        where_clause_grp = TokenGroup([token, ], ST.WhereClause)

        while token_group.ttype not in (ST.FromClause, ):
            # Get out of the Token Group until you find preceeding From Clause
            token_group = self._switch_to_parent(token_group)

        # Get out of the Clause Token Group and exit
        token_group = self._switch_to_parent(token_group)
        token_group.append(where_clause_grp)
        return where_clause_grp

    def _process_group_by_clause(self, stmt, token_group, token):
        group_by_clause_grp = TokenGroup([token, ], ST.GroupByClause)

        while token_group.ttype not in (ST.FromClause, ST.WhereClause):
            # Get out of the Token Group until you find preceeding From / Where Clause
            token_group = self._switch_to_parent(token_group)

        # Get out of the Clause Token Group and exit
        token_group = self._switch_to_parent(token_group)
        token_group.append(group_by_clause_grp)
        return group_by_clause_grp

    def _process_having_clause(self, stmt, token_group, token):
        having_clause_grp = TokenGroup([token, ], ST.HavingClause)

        while token_group.ttype not in (ST.FromClause, ST.WhereClause, ST.GroupByClause):
            # NOTE: Having Clause need not require Group By Clause before it
            # Get out of the Token Group until you find preceeding From / Where / Group By Clause
            token_group = self._switch_to_parent(token_group)

        # Get out of the Clause Token Group and exit
        token_group = self._switch_to_parent(token_group)
        token_group.append(having_clause_grp)
        return having_clause_grp

    def _process_order_by_clause(self, stmt, token_group, token):
        order_by_clause_grp = TokenGroup([token, ], ST.OrderByClause)

        while token_group.ttype not in (ST.FromClause, ST.WhereClause, ST.GroupByClause, ST.HavingClause):
            # Get out of the Token Group until you find preceeding Where / Group By / Having Clause
            token_group = self._switch_to_parent(token_group)

        # Get out of the Clause Token Group and exit
        token_group = self._switch_to_parent(token_group)
        token_group.append(order_by_clause_grp)
        return order_by_clause_grp

    def _process_join(self, stmt, token_group, token):
        while token_group.ttype != ST.FromClause:
            # Get out of the Token Group until you find the matching From Clause
            token_group = self._switch_to_parent(token_group)
        token_group.append(token)
        return token_group

    def _process_on(self, stmt, token_group, token):
        join_on_grp = TokenGroup([token, ], ST.JoinOnClause)
        while token_group.ttype != ST.FromClause:
            # Get out of the Token Group until you find the matching From Clause
            token_group = self._switch_to_parent(token_group)
        token_group.append(join_on_grp)
        return join_on_grp

    def _process_and(self, stmt, token_group, token):
        token.ttype = ST.LogicalOperator
        while token_group.ttype not in (ST.JoinOnClause, ST.WhereClause, ST.HavingClause,
                                        ST.ConditionGroup, ST.Between, ST.NotBetween,
                                        ST.CaseExpression, ST.WhenExpression, ST.ThenExpression, ST.ElseExpression):
            # Get out of the Token Group until you find preceeding Join On, Where, Having Clause
            token_group = self._switch_to_parent(token_group)
        if token_group.ttype in (ST.Between, ST.NotBetween) and token_group.has_token_as_immediate_child(token):
            # Between Clause should not have more than one AND Operator
            # Get out of the Token Group until you find preceeding Where, Having Clause
            token_group = self._switch_to_parent(token_group)
            return self._process_and(stmt, token_group, token)
        token_group.append(token)
        return token_group

    def _process_or(self, stmt, token_group, token):
        token.ttype = ST.LogicalOperator
        while token_group.ttype not in (ST.JoinOnClause, ST.WhereClause, ST.HavingClause,
                                        ST.ConditionGroup, ST.Between, ST.NotBetween,
                                        ST.CaseExpression, ST.WhenExpression, ST.ThenExpression, ST.ElseExpression):
            # Get out of the Token Group until you find preceeding Join On, Where, Having Clause
            token_group = self._switch_to_parent(token_group)
        token_group.append(token)
        return token_group

    def _process_in(self, stmt, token_group, token):
        while token_group.ttype not in (ST.JoinOnClause, ST.WhereClause, ST.HavingClause,
                                        ST.Condition, ST.RoundBracket, ST.ConditionGroup, ST.Not,
                                        ST.CaseExpression, ST.WhenExpression, ST.ThenExpression, ST.ElseExpression):
            # Get out of the Token Group until you find Condition Clause
            token_group = self._switch_to_parent(token_group)
        if token_group.ttype == ST.RoundBracket:
            token_group.ttype = ST.ConditionGroup
        if token_group.ttype == ST.Condition:
            # This will mostly be NOT IN Condition
            token_group.ttype = ST.NotIn if token_group.last_token().match_type_value(
                Token(ST.LogicalOperator, 'NOT')) else ST.In
        else:
            token_group = token_group.merge_into_token_group(
                ST.In, token_list_start_index_included=token_group.last_token_index())
        token_group.append(token)
        return token_group

    def _process_like(self, stmt, token_group, token):
        # LIKE is same as IN, just that the ttype should be Like/NotLike
        token_group = self._process_in(stmt, token_group, token)
        token_group.ttype = ST.Like if token_group.ttype == ST.In else ST.NotLike
        return token_group

    def _process_between(self, stmt, token_group, token):
        # BETWEEN is same as IN, just that the ttype should be Between/NotBetween
        token_group = self._process_in(stmt, token_group, token)
        token_group.ttype = ST.Between if token_group.ttype == ST.In else ST.NotBetween
        return token_group

    def _process_is(self, stmt, token_group, token):
        # IS is same as IN, just that the ttype should be Comparison
        token_group = self._process_in(stmt, token_group, token)
        token_group.ttype = ST.Comparison
        return token_group

    def _process_into(self, stmt, token_group, token):
        # Assumption: INTO Clause will never be in a Sub-Query
        while token_group.ttype not in (ST.InsertIntoClause, ST.SelectClause):
            # Get out of the Token Group until you find preceeding
            # (Insert Into Clause, Select Clause)
            token_group = self._switch_to_parent(token_group)
        if token_group.ttype == ST.InsertIntoClause:
            # INSERT INTO statement, just append INTO Keyword
            token_group.append(token)
        elif token_group.ttype == ST.SelectClause and token_group.parent == stmt:
            # Topmost Select Statement which should now be Select Into Statement
            stmt.ttype = ST.SelectInto
            token_group = self._switch_to_parent(token_group)
            into_clause_grp = TokenGroup([token, ], ST.SelectIntoClause)
            token_group.append(into_clause_grp)
            token_group = into_clause_grp

        return token_group

    def _process_not(self, stmt, token_group, token):
        # TODO: NOT can be in SELECT Clause as well
        # TODO: IS Condition
        token.ttype = ST.LogicalOperator
        while token_group.ttype not in (ST.JoinOnClause, ST.WhereClause, ST.HavingClause,
                                        ST.ConditionGroup, ST.RoundBracket, ST.Comparison,
                                        ST.CaseExpression, ST.WhenExpression, ST.ThenExpression, ST.ElseExpression):
            # Get out of the Token Group until you find Where, JoinOn, Having Clause or ConditionGroup
            token_group = self._switch_to_parent(token_group)
        if token_group.ttype == ST.RoundBracket:
            token_group.ttype = ST.ConditionGroup
        if token_group.last_token().ttype not in (ST.Identifier, ST.ComputedIdentifier, ST.Function):
            not_condition_grp = TokenGroup([token, ], ST.Not)
            token_group.append(not_condition_grp)
            return not_condition_grp
        else:
            # This is the ST.Condition or ST.Comparison Token Group
            token_group = token_group.merge_into_token_group(
                ST.Condition, token_list_start_index_included=token_group.last_token_index())
            token_group.append(token)
            return token_group

    def _process_as(self, stmt, token_group, token):
        if token_group.ttype == ST.SelectClause:
            # Case: SELECT CASE ... END AS case_alias
            token_group = token_group.merge_into_token_group(
                ST.ComputedIdentifier, token_list_start_index_included=token_group.last_token_index())
        else:
            while token_group.parent.ttype not in (ST.SelectClause, ST.FromClause):
                token_group = self._switch_to_parent(token_group)
        token_group.append(token)
        return token_group

    def _process_case(self, stmt, token_group, token):
        case_exp_grp = TokenGroup([token, ], ST.CaseExpression)
        while token_group.ttype not in (ST.SelectClause, ST.JoinOnClause, ST.WhereClause, ST.HavingClause,
                                        ST.ConditionGroup, ST.Condition, ST.RoundBracket, ST.Not,
                                        ST.CaseExpression, ST.WhenExpression, ST.ThenExpression, ST.ElseExpression):
            # TODO: Might need to consider ComputedIdentifier Case
            # Get out of the Token Group until you find appropriate Clause
            token_group = self._switch_to_parent(token_group)
        token_group.append(case_exp_grp)
        return case_exp_grp

    def _process_when(self, stmt, token_group, token):
        when_exp_grp = TokenGroup([token, ], ST.WhenExpression)
        while token_group.ttype not in (ST.CaseExpression):
            # Get out of the Token Group until you find Case Expression
            token_group = self._switch_to_parent(token_group)
        token_group.append(when_exp_grp)
        return when_exp_grp

    def _process_then(self, stmt, token_group, token):
        then_exp_grp = TokenGroup([token, ], ST.ThenExpression)
        while token_group.ttype not in (ST.WhenExpression):
            # Get out of the Token Group until you find When Expression
            token_group = self._switch_to_parent(token_group)
        token_group.append(then_exp_grp)
        return then_exp_grp

    def _process_else(self, stmt, token_group, token):
        else_exp_grp = TokenGroup([token, ], ST.ElseExpression)
        while token_group.ttype not in (ST.CaseExpression):
            # Get out of the Token Group until you find Case Expression
            token_group = self._switch_to_parent(token_group)
        token_group.append(else_exp_grp)
        return else_exp_grp

    def _process_end(self, stmt, token_group, token):
        while token_group.ttype not in (ST.CaseExpression):
            # Get out of the Token Group until you find Case Expression
            token_group = self._switch_to_parent(token_group)
        token_group.append(token)
        token_group = self._switch_to_parent(token_group)
        return token_group

    def _process_literal_number(self, stmt, token_group, token):
        if token_group.ttype == ST.SelectClause:
            select_constant_identifier_grp = TokenGroup(
                [token, ], ST.SelectConstantIdentifier)
            token_group.append(select_constant_identifier_grp)
            token_group = select_constant_identifier_grp
        else:
            token_group.append(token)
        return token_group

    def _process_literal_string(self, stmt, token_group, token):
        token.ttype = T.String
        if token_group.ttype == ST.SelectClause:
            select_constant_identifier_grp = TokenGroup(
                [token, ], ST.SelectConstantIdentifier)
            token_group.append(select_constant_identifier_grp)
            token_group = select_constant_identifier_grp
        elif token_group.token_list[-1].ttype == T.String:
            setattr(token_group.token_list[-1], '_value',
                    token_group.token_list[-1].value() + token.value())
        else:
            token_group.append(token)
        return token_group

    def _process_name(self, stmt, token_group, token):
        raise NotImplementedError

    def _process_punctuation(self, stmt, token_group, token):
        raise NotImplementedError

    def _process_operator(self, stmt, token_group, token):
        raise NotImplementedError

    def _set_rules_(self):
        ''' You may extend this function in Child classes
        '''
        return {
            'Token.Comment.Single': None,
            'Token.Comment.Multiline': None,
            'Token.Text.Whitespace': None,
            'Token.Text.Name': self._process_name,
            'Token.Text.Punctuation': self._process_punctuation,
            'Token.Text.Operator': self._process_operator,
            'Token.Keyword.SELECT': self._process_select_clause,
            'Token.Keyword.DISTINCT': None,
            'Token.Keyword.FROM': self._process_from_clause,
            'Token.Keyword.WHERE': self._process_where_clause,
            'Token.Keyword.GROUP': self._process_group_by_clause,
            'Token.Keyword.HAVING': self._process_having_clause,
            'Token.Keyword.ORDER': self._process_order_by_clause,
            'Token.Keyword.BY': None,
            'Token.Keyword.JOIN': self._process_join,
            'Token.Keyword.INNER': self._process_join,
            'Token.Keyword.LEFT': self._process_join,
            'Token.Keyword.RIGHT': self._process_join,
            'Token.Keyword.FULL': self._process_join,
            'Token.Keyword.OUTER': self._process_join,
            'Token.Keyword.CROSS': self._process_join,
            'Token.Keyword.ON': self._process_on,
            'Token.Keyword.AND': self._process_and,
            'Token.Keyword.OR': self._process_or,
            'Token.Keyword.IN': self._process_in,
            'Token.Keyword.LIKE': self._process_like,
            'Token.Keyword.BETWEEN': self._process_between,
            'Token.Keyword.IS': self._process_is,
            'Token.Keyword.AS': self._process_as,
            'Token.Keyword.INTO': self._process_into,
            'Token.Keyword.NOT': self._process_not,
            'Token.Keyword.CASE': self._process_case,
            'Token.Keyword.WHEN': self._process_when,
            'Token.Keyword.THEN': self._process_then,
            'Token.Keyword.ELSE': self._process_else,
            'Token.Keyword.END': self._process_end,
            'Token.Literal.Number': self._process_literal_number,
            'Token.Literal.String': self._process_literal_string,
        }
