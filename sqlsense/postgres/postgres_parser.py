from pygments import token as T
from pygments.lexers.sql import PostgresLexer

import sqlsense.postgres.postgres_tokens as PT
import sqlsense.tokens as ST
from sqlsense.filter import float_to_integer_token, float_to_punctuation_token
from sqlsense.parser import SqlParser
from sqlsense.postgres.postgres_sql import PostgresSqlStatement
from sqlsense.sql import Token, TokenGroup


class PostgresParser(SqlParser):
    def __init__(self):
        super().__init__(lexer_object=PostgresLexer)
        self._lexer.add_filter(float_to_integer_token())
        self._lexer.add_filter(float_to_punctuation_token())

    def _get_sql_statement(self):
        return PostgresSqlStatement()

    def _process_name(self, stmt, token_group, token, tokengroup_set):
        if token_group.last_token().match_type_value(Token(T.Keyword, 'AS')):
            # Alias follows AS Keyword
            token.ttype = ST.AliasName
            token_group.append(token)
        elif (token_group.parent.ttype in (ST.SelectClause, ST.FromClause) and
              ((token_group.ttype == ST.Identifier and token_group.last_token().ttype == T.Name) or
               (token_group.ttype == ST.Function and token_group.last_token().ttype == ST.ArgumentList) or
               (token_group.ttype == ST.SubQuery and token_group.last_token().match_type_value(Token(T.Punctuation, ')'))) or
               (token_group.ttype == ST.ComputedIdentifier and token_group.last_token().ttype != T.Operator) or
               token_group.ttype == ST.SelectConstantIdentifier)):
            # Alias withot AS Keyword. Here TokenGroup has to be direct child of Select/From clause
            # and must satisfy other appropriate conditions
            token.ttype = ST.AliasName
            token_group.append(token)
        elif (token_group.parent.ttype == ST.ComputedIdentifier and
              token_group.ttype == ST.Identifier and token_group.last_token().ttype == T.Name):
            # Case: SELECT A.x+B.y SomeAlias FROM ...
            # here Computed Identifier => A.x+B.y and Identifier => B.y followed by Alias
            return self._process_name(stmt, self._switch_to_parent(token_group), token, tokengroup_set)
        elif (token_group.ttype == ST.SelectClause and token_group.last_token().ttype not in (T.Keyword, T.Punctuation)):
            # Case: SELECT CASE ... END AS case_alias
            token_group = token_group.merge_into_token_group(
                ST.ComputedIdentifier, token_list_start_index_included=token_group.last_token_index())
            token.ttype = ST.AliasName
            token_group.append(token)
        elif token_group.ttype == ST.Identifier:
            token_group.append(token)
        else:
            identifier_grp = TokenGroup([token, ], ST.Identifier)
            token_group.append(identifier_grp)
            token_group = identifier_grp
        return token_group

    def _process_punctuation(self, stmt, token_group, token, tokengroup_set):
        if token.value() == '(':
            # Open a New Sub Query Token Group
            bracket_grp = TokenGroup([token, ], ST.RoundBracket)
            if token_group.ttype == ST.Identifier and token_group.last_token().ttype == T.Name:
                # This is actually a Function Identifier
                # TODO: Maybe this should be a sub group
                # Identifier.Function instead of just Identifier
                token_group.ttype = ST.Function
                # Function Argument List instead of Sub-Query
                bracket_grp.ttype = ST.ArgumentList
            elif token_group.ttype in (ST.In, ST.NotIn):
                # This can be the CollectionSet or SubQuery (ttype will set to SubQuery in subsequent steps).
                bracket_grp.ttype = ST.CollectionSet
            token_group.append(bracket_grp)
            token_group = bracket_grp
        elif token.value() == ')':
            while token_group.ttype not in (ST.RoundBracket, ST.ArgumentList, ST.SubQuery, ST.CollectionSet, ST.ConditionGroup):
                # Get out of the Token Group until you find the matching opening bracket
                token_group = self._switch_to_parent(token_group)
            token_group.append(token)
            if token_group.ttype == ST.RoundBracket and token_group.parent.ttype == ST.SelectClause:
                token_group = token_group.parent.merge_into_token_group(
                    ST.ComputedIdentifier, token_list_start_index_included=token_group.parent.last_token_index())
            elif token_group.ttype != ST.SubQuery:
                token_group = self._switch_to_parent(token_group)
        elif token.value() == '.':
            # table.column, alias.column (in general QualifierName<QualifierOperator>Name)
            token_group.last_token().ttype = ST.QualifierName
            token.ttype = ST.QualifierOperator
            token_group.append(token)
        elif token.value() == ',':
            if token_group.ttype in (ST.Identifier, ST.ComputedIdentifier, ST.SelectConstantIdentifier, ST.Function, ST.CaseExpression):
                # Get out of the Token Group, so that we can create another Identifier
                token_group = self._switch_to_parent(token_group)
            token_group.append(token)
        return token_group

    def _process_operator(self, stmt, token_group, token, tokengroup_set):
        if token.value() == '*':
            # * can be a Wildcard in Select Clause
            if (token_group.ttype == ST.SelectClause or
                    (token_group.ttype in (ST.Identifier, ) and token_group.last_token().ttype == ST.QualifierOperator)):
                # SELECT * FROM ...
                # SELECT table.* FROM ... or SELECT alias.* FROM ...
                # TODO: Is it true for Identifier.Function?
                token.ttype = ST.AllColumnsIdentifier   # instead of Operator
                token_group.append(token)
            else:
                token_group = self._setup_computed_identifier(
                    stmt, token_group, token)
        elif token.value() in ('=', '!=', '<>', '<', '<=', '>', '>='):
            token.ttype = ST.ComparisonOperator
            while token_group.ttype not in (ST.RoundBracket, ST.ConditionGroup, ST.JoinOnClause, ST.WhereClause, ST.HavingClause, ST.Not,
                                            ST.CaseExpression, ST.WhenExpression, ST.ThenExpression, ST.ElseExpression):
                # Get out of the Token Group until you find the matching Condition Clause
                token_group = self._switch_to_parent(token_group)
            if token_group.ttype in (ST.RoundBracket):
                token_group.ttype = ST.ConditionGroup
            token_group = token_group.merge_into_token_group(
                ST.Comparison, token_list_start_index_included=token_group.last_token_index())
            token_group.append(token)
        elif token.value() in ('+', '-', '*', '/', '%', '^'):  # * is already taken care of
            token_group = self._setup_computed_identifier(
                stmt, token_group, token)
        return token_group

    def _process_limit(self, stmt, token_group, token, tokengroup_set):
        # Assumption: LIMIT will be at SELECT Statement Level
        limit_clause_grp = TokenGroup([token, ], PT.LimitClause)
        while token_group.ttype not in (ST.Select, ST.SelectInto, ST.InsertIntoSelect, ST.SubQuery):
            token_group = self._switch_to_parent(token_group)
        token_group.append(limit_clause_grp)
        return limit_clause_grp

    def _process_keyword_name(self, stmt, token_group, token, tokengroup_set):
        token.ttype = T.Name
        return self._process_name(stmt, token_group, token, tokengroup_set)

    def _set_rules_(self):
        ''' You may extend this function in Child classes
        '''
        rules_dict = super()._set_rules_()
        rules_dict['Token.Name'] = (self._process_name, None)
        rules_dict['Token.Punctuation'] = (self._process_punctuation, None)
        rules_dict['Token.Operator'] = (self._process_operator, None)
        rules_dict['Token.Keyword.LIMIT'] = (self._process_limit, None)
        rules_dict['Token.Keyword.NAME'] = (self._process_keyword_name, None)
        return rules_dict
