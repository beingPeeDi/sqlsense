import unittest

from pygments import token as T

import sqlsense.postgres.postgres_tokens as PT
import sqlsense.tokens as ST
from sqlsense.postgres.postgres_parser import PostgresParser
from sqlsense.postgres.postgres_sql import PostgresSqlStatement
from sqlsense.sql import Token, TokenGroup


def get_token(ttype, value):
    return Token(ttype, value)


def _token_list_tracing_helper(tkg, exp_tkg, ident='\t'):
    i = 0
    for tk in tkg.token_list:
        print('.{0}--> {1}: <{2}>'.format(ident, tk.ttype, tk.value()))
        print('.{0}==> {1}: <{2}>'.format(
            ident, exp_tkg.token_list[i].ttype, exp_tkg.token_list[i].value()))
        assert tk.ttype == exp_tkg.token_list[i].ttype and tk.value(
        ) == exp_tkg.token_list[i].value()
        if isinstance(tk, TokenGroup):
            _token_list_tracing_helper(tk, exp_tkg.token_list[i], ident + '\t')
        i += 1
    assert i == len(exp_tkg.token_list)


class SelectStatementTest(unittest.TestCase):

    # SELECT [ ALL | DISTINCT ] [ FIRST | TOP number-of-rows ] select-list|*
    # … [ INTO { host-variable-list | variable-list | table-name } ]
    # … [ FROM table-list ]
    # … [ WHERE search-condition ]
    # … [ GROUP BY [ expression [, …]
    # … [ HAVING search-condition ]
    # … [ ORDER BY { expression | integer } [ ASC | DESC ] [, …] ]

    def test_001_from_join(self):
        p = PostgresParser()
        sql_text = '''
        --- some comment

        select upper(a.c) as c,   p.*
        from abc.a_table as a join long_table_name p
        on a.z = p.z;
        '''
        exp_stmt = [
            PostgresSqlStatement(ttype=ST.Select, token_list=[
                get_token(T.Comment.Single, '--- some comment\n'),
                get_token(T.Whitespace, ' '),

                TokenGroup(ttype=ST.SelectClause, token_list=[
                    get_token(T.Keyword, 'SELECT'),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.Function, token_list=[
                        get_token(T.Name, 'upper'),
                        TokenGroup(ttype=ST.ArgumentList, token_list=[
                            get_token(T.Punctuation, '('),
                            TokenGroup(ttype=ST.Identifier, token_list=[
                                get_token(ST.QualifierName, 'a'),
                                get_token(ST.QualifierOperator, '.'),
                                get_token(T.Name, 'c'),
                            ]),
                            get_token(T.Punctuation, ')')
                        ]),
                        get_token(T.Whitespace, ' '),
                        get_token(T.Keyword, 'AS'),
                        get_token(T.Whitespace, ' '),
                        get_token(ST.AliasName, 'c'),
                    ]),
                    get_token(T.Punctuation, ','),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.Identifier, token_list=[
                        get_token(ST.QualifierName, 'p'),
                        get_token(ST.QualifierOperator, '.'),
                        get_token(ST.AllColumnsIdentifier, '*'),
                    ]),
                ]),

                get_token(T.Whitespace, ' '),

                TokenGroup(ttype=ST.FromClause, token_list=[
                    get_token(T.Keyword, 'FROM'),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.Identifier, token_list=[
                        get_token(ST.QualifierName, 'abc'),
                        get_token(ST.QualifierOperator, '.'),
                        get_token(T.Name, 'a_table'),
                        get_token(T.Whitespace, ' '),
                        get_token(T.Keyword, 'AS'),
                        get_token(T.Whitespace, ' '),
                        get_token(ST.AliasName, 'a'),
                    ]),
                    get_token(T.Whitespace, ' '),
                    get_token(T.Keyword, 'JOIN'),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.Identifier, token_list=[
                        get_token(T.Name, 'long_table_name'),
                        get_token(T.Whitespace, ' '),
                        get_token(ST.AliasName, 'p'),
                    ]),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.JoinOnClause, token_list=[
                        get_token(T.Keyword, 'ON'),
                        get_token(T.Whitespace, ' '),
                        TokenGroup(ttype=ST.Comparison, token_list=[
                            TokenGroup(ttype=ST.Identifier, token_list=[
                                get_token(ST.QualifierName, 'a'),
                                get_token(ST.QualifierOperator, '.'),
                                get_token(T.Name, 'z'),
                            ]),
                            get_token(T.Whitespace, ' '),
                            get_token(ST.ComparisonOperator, '='),
                            get_token(T.Whitespace, ' '),
                            TokenGroup(ttype=ST.Identifier, token_list=[
                                get_token(ST.QualifierName, 'p'),
                                get_token(ST.QualifierOperator, '.'),
                                get_token(T.Name, 'z'),
                            ]),
                        ]),
                    ]),
                ]),

                get_token(T.Punctuation, ';'),
            ]),
        ]
        i = 0
        print('--')
        print(sql_text)
        print('--')
        for x in p.parse(sql_text):
            _token_list_tracing_helper(x, exp_stmt[i])
            i += 1
        assert i == len(exp_stmt)
        print('')

    def test_002_subquery_in_from_join(self):
        p = PostgresParser()
        sql_text = '''
        --- some comment

        select upper(abc.c)   c,       xyz.*
        from abc join (select * from subtable) xyz
        on abc.z = xyz.z;
        '''
        exp_stmt = [
            PostgresSqlStatement(ttype=ST.Select, token_list=[
                get_token(T.Comment.Single, '--- some comment\n'),
                get_token(T.Whitespace, ' '),

                TokenGroup(ttype=ST.SelectClause, token_list=[
                    get_token(T.Keyword, 'SELECT'),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.Function, token_list=[
                        get_token(T.Name, 'upper'),
                        TokenGroup(ttype=ST.ArgumentList, token_list=[
                            get_token(T.Punctuation, '('),
                            TokenGroup(ttype=ST.Identifier, token_list=[
                                get_token(ST.QualifierName, 'abc'),
                                get_token(ST.QualifierOperator, '.'),
                                get_token(T.Name, 'c'),
                            ]),
                            get_token(T.Punctuation, ')')
                        ]),
                        get_token(T.Whitespace, ' '),
                        get_token(ST.AliasName, 'c'),
                    ]),
                    get_token(T.Punctuation, ','),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.Identifier, token_list=[
                        get_token(ST.QualifierName, 'xyz'),
                        get_token(ST.QualifierOperator, '.'),
                        get_token(ST.AllColumnsIdentifier, '*'),
                    ]),
                ]),

                get_token(T.Whitespace, ' '),

                TokenGroup(ttype=ST.FromClause, token_list=[
                    get_token(T.Keyword, 'FROM'),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.Identifier, token_list=[
                        get_token(T.Name, 'abc'),
                    ]),
                    get_token(T.Whitespace, ' '),
                    get_token(T.Keyword, 'JOIN'),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.SubQuery, token_list=[
                        get_token(T.Punctuation, '('),
                        TokenGroup(ttype=ST.SelectClause, token_list=[
                            get_token(T.Keyword, 'SELECT'),
                            get_token(T.Whitespace, ' '),
                            get_token(ST.AllColumnsIdentifier, '*'),
                        ]),
                        get_token(T.Whitespace, ' '),
                        TokenGroup(ttype=ST.FromClause, token_list=[
                            get_token(T.Keyword, 'FROM'),
                            get_token(T.Whitespace, ' '),
                            TokenGroup(ttype=ST.Identifier, token_list=[
                                get_token(T.Name, 'subtable'),
                            ]),
                        ]),
                        get_token(T.Punctuation, ')'),
                        get_token(T.Whitespace, ' '),
                        get_token(ST.AliasName, 'xyz'),
                    ]),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.JoinOnClause, token_list=[
                        get_token(T.Keyword, 'ON'),
                        get_token(T.Whitespace, ' '),
                        TokenGroup(ttype=ST.Comparison, token_list=[
                            TokenGroup(ttype=ST.Identifier, token_list=[
                                get_token(ST.QualifierName, 'abc'),
                                get_token(ST.QualifierOperator, '.'),
                                get_token(T.Name, 'z'),
                            ]),
                            get_token(T.Whitespace, ' '),
                            get_token(ST.ComparisonOperator, '='),
                            get_token(T.Whitespace, ' '),
                            TokenGroup(ttype=ST.Identifier, token_list=[
                                get_token(ST.QualifierName, 'xyz'),
                                get_token(ST.QualifierOperator, '.'),
                                get_token(T.Name, 'z'),
                            ]),
                        ]),
                    ]),
                ]),

                get_token(T.Punctuation, ';'),
            ]),
        ]
        i = 0
        print('--')
        print(sql_text)
        print('--')
        for x in p.parse(sql_text):
            _token_list_tracing_helper(x, exp_stmt[i])
            i += 1
        assert i == len(exp_stmt)
        print('')

    def test_003_where_in_condt(self):
        p = PostgresParser()
        sql_text = '''
        select add_nums(abc.c, 5) as c,       xyz.*
        from abc join (select * from subtable) as xyz
        on abc.z = xyz.z -- comments in between
        where xyz.x >= 20.5
        and abc.p in (select j from where_in_table);
        '''
        exp_stmt = [
            PostgresSqlStatement(ttype=ST.Select, token_list=[
                TokenGroup(ttype=ST.SelectClause, token_list=[
                    get_token(T.Keyword, 'SELECT'),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.Function, token_list=[
                        get_token(T.Name, 'add_nums'),
                        TokenGroup(ttype=ST.ArgumentList, token_list=[
                            get_token(T.Punctuation, '('),
                            TokenGroup(ttype=ST.Identifier, token_list=[
                                get_token(ST.QualifierName, 'abc'),
                                get_token(ST.QualifierOperator, '.'),
                                get_token(T.Name, 'c'),
                            ]),
                            get_token(T.Punctuation, ','),
                            get_token(T.Whitespace, ' '),
                            get_token(T.Number.Integer, '5'),
                            get_token(T.Punctuation, ')')
                        ]),
                        get_token(T.Whitespace, ' '),
                        get_token(T.Keyword, 'AS'),
                        get_token(T.Whitespace, ' '),
                        get_token(ST.AliasName, 'c'),
                    ]),
                    get_token(T.Punctuation, ','),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.Identifier, token_list=[
                        get_token(ST.QualifierName, 'xyz'),
                        get_token(ST.QualifierOperator, '.'),
                        get_token(ST.AllColumnsIdentifier, '*'),
                    ]),
                ]),

                get_token(T.Whitespace, ' '),

                TokenGroup(ttype=ST.FromClause, token_list=[
                    get_token(T.Keyword, 'FROM'),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.Identifier, token_list=[
                        get_token(T.Name, 'abc'),
                    ]),
                    get_token(T.Whitespace, ' '),
                    get_token(T.Keyword, 'JOIN'),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.SubQuery, token_list=[
                        get_token(T.Punctuation, '('),
                        TokenGroup(ttype=ST.SelectClause, token_list=[
                            get_token(T.Keyword, 'SELECT'),
                            get_token(T.Whitespace, ' '),
                            get_token(ST.AllColumnsIdentifier, '*'),
                        ]),
                        get_token(T.Whitespace, ' '),
                        TokenGroup(ttype=ST.FromClause, token_list=[
                            get_token(T.Keyword, 'FROM'),
                            get_token(T.Whitespace, ' '),
                            TokenGroup(ttype=ST.Identifier, token_list=[
                                get_token(T.Name, 'subtable'),
                            ]),
                        ]),
                        get_token(T.Punctuation, ')'),
                        get_token(T.Whitespace, ' '),
                        get_token(T.Keyword, 'AS'),
                        get_token(T.Whitespace, ' '),
                        get_token(ST.AliasName, 'xyz'),
                    ]),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.JoinOnClause, token_list=[
                        get_token(T.Keyword, 'ON'),
                        get_token(T.Whitespace, ' '),
                        TokenGroup(ttype=ST.Comparison, token_list=[
                            TokenGroup(ttype=ST.Identifier, token_list=[
                                get_token(ST.QualifierName, 'abc'),
                                get_token(ST.QualifierOperator, '.'),
                                get_token(T.Name, 'z'),
                            ]),
                            get_token(T.Whitespace, ' '),
                            get_token(ST.ComparisonOperator, '='),
                            get_token(T.Whitespace, ' '),
                            TokenGroup(ttype=ST.Identifier, token_list=[
                                get_token(ST.QualifierName, 'xyz'),
                                get_token(ST.QualifierOperator, '.'),
                                get_token(T.Name, 'z'),
                                get_token(T.Whitespace, ' '),
                                get_token(T.Comment.Single,
                                          '-- comments in between\n')
                            ]),
                        ]),
                    ]),
                ]),

                get_token(T.Whitespace, ' '),

                TokenGroup(ttype=ST.WhereClause, token_list=[
                    get_token(T.Keyword, 'WHERE'),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.Comparison, token_list=[
                        TokenGroup(ttype=ST.Identifier, token_list=[
                            get_token(ST.QualifierName, 'xyz'),
                            get_token(ST.QualifierOperator, '.'),
                            get_token(T.Name, 'x'),
                        ]),
                        get_token(T.Whitespace, ' '),
                        get_token(ST.ComparisonOperator, '>='),
                        get_token(T.Whitespace, ' '),
                        get_token(T.Number.Float, '20.5'),
                    ]),
                    get_token(T.Whitespace, ' '),
                    get_token(ST.LogicalOperator, 'AND'),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.In, token_list=[
                        TokenGroup(ttype=ST.Identifier, token_list=[
                            get_token(ST.QualifierName, 'abc'),
                            get_token(ST.QualifierOperator, '.'),
                            get_token(T.Name, 'p'),
                        ]),
                        get_token(T.Whitespace, ' '),
                        get_token(T.Keyword, 'IN'),
                        get_token(T.Whitespace, ' '),
                        TokenGroup(ttype=ST.SubQuery, token_list=[
                            get_token(T.Punctuation, '('),
                            TokenGroup(ttype=ST.SelectClause, token_list=[
                                get_token(T.Keyword, 'SELECT'),
                                get_token(T.Whitespace, ' '),
                                TokenGroup(ttype=ST.Identifier, token_list=[
                                    get_token(T.Name, 'j'),
                                ]),
                            ]),
                            get_token(T.Whitespace, ' '),
                            TokenGroup(ttype=ST.FromClause, token_list=[
                                get_token(T.Keyword, 'FROM'),
                                get_token(T.Whitespace, ' '),
                                TokenGroup(ttype=ST.Identifier, token_list=[
                                    get_token(T.Name, 'where_in_table'),
                                ]),
                            ]),
                            get_token(T.Punctuation, ')'),
                        ]),
                    ]),
                ]),

                get_token(T.Punctuation, ';'),
            ]),
        ]
        i = 0
        print('--')
        print(sql_text)
        print('--')
        for x in p.parse(sql_text):
            _token_list_tracing_helper(x, exp_stmt[i])
            i += 1
        assert i == len(exp_stmt)
        print('')

    def test_004_not_null_condt_and_group_by(self):
        p = PostgresParser()
        sql_text = '''
        select upper(abc.c) as c,
               count(xyz.*) total_count
        from abc join (select * from subtable where some_col is not null) xyz
        on abc.z = xyz.z -- comments in between
        where xyz.x >= 20.5
        and abc.p in (select j from where_in_table)
        group by abc.c;
        '''
        exp_stmt = [
            PostgresSqlStatement(ttype=ST.Select, token_list=[
                TokenGroup(ttype=ST.SelectClause, token_list=[
                    get_token(T.Keyword, 'SELECT'),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.Function, token_list=[
                        get_token(T.Name, 'upper'),
                        TokenGroup(ttype=ST.ArgumentList, token_list=[
                            get_token(T.Punctuation, '('),
                            TokenGroup(ttype=ST.Identifier, token_list=[
                                get_token(ST.QualifierName, 'abc'),
                                get_token(ST.QualifierOperator, '.'),
                                get_token(T.Name, 'c'),
                            ]),
                            get_token(T.Punctuation, ')')
                        ]),
                        get_token(T.Whitespace, ' '),
                        get_token(T.Keyword, 'AS'),
                        get_token(T.Whitespace, ' '),
                        get_token(ST.AliasName, 'c'),
                    ]),
                    get_token(T.Punctuation, ','),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.Function, token_list=[
                        get_token(T.Name, 'count'),
                        TokenGroup(ttype=ST.ArgumentList, token_list=[
                            get_token(T.Punctuation, '('),
                            TokenGroup(ttype=ST.Identifier, token_list=[
                                get_token(ST.QualifierName, 'xyz'),
                                get_token(ST.QualifierOperator, '.'),
                                get_token(ST.AllColumnsIdentifier, '*'),
                            ]),
                            get_token(T.Punctuation, ')')
                        ]),
                        get_token(T.Whitespace, ' '),
                        get_token(ST.AliasName, 'total_count'),
                    ]),
                ]),

                get_token(T.Whitespace, ' '),

                TokenGroup(ttype=ST.FromClause, token_list=[
                    get_token(T.Keyword, 'FROM'),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.Identifier, token_list=[
                        get_token(T.Name, 'abc'),
                    ]),
                    get_token(T.Whitespace, ' '),
                    get_token(T.Keyword, 'JOIN'),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.SubQuery, token_list=[
                        get_token(T.Punctuation, '('),
                        TokenGroup(ttype=ST.SelectClause, token_list=[
                            get_token(T.Keyword, 'SELECT'),
                            get_token(T.Whitespace, ' '),
                            get_token(ST.AllColumnsIdentifier, '*'),
                        ]),
                        get_token(T.Whitespace, ' '),
                        TokenGroup(ttype=ST.FromClause, token_list=[
                            get_token(T.Keyword, 'FROM'),
                            get_token(T.Whitespace, ' '),
                            TokenGroup(ttype=ST.Identifier, token_list=[
                                get_token(T.Name, 'subtable'),
                            ]),
                        ]),
                        get_token(T.Whitespace, ' '),
                        TokenGroup(ttype=ST.WhereClause, token_list=[
                            get_token(T.Keyword, 'WHERE'),
                            get_token(T.Whitespace, ' '),
                            TokenGroup(ttype=ST.Comparison, token_list=[
                                TokenGroup(ttype=ST.Identifier, token_list=[
                                    get_token(T.Name, 'some_col'),
                                ]),
                                get_token(T.Whitespace, ' '),
                                get_token(T.Keyword, 'IS'),
                                get_token(T.Whitespace, ' '),
                                TokenGroup(ttype=ST.Not, token_list=[
                                    get_token(ST.LogicalOperator, 'NOT'),
                                    get_token(T.Whitespace, ' '),
                                    get_token(T.Keyword, 'NULL'),
                                ]),
                            ]),
                        ]),
                        get_token(T.Punctuation, ')'),
                        get_token(T.Whitespace, ' '),
                        get_token(ST.AliasName, 'xyz'),
                    ]),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.JoinOnClause, token_list=[
                        get_token(T.Keyword, 'ON'),
                        get_token(T.Whitespace, ' '),
                        TokenGroup(ttype=ST.Comparison, token_list=[
                            TokenGroup(ttype=ST.Identifier, token_list=[
                                get_token(ST.QualifierName, 'abc'),
                                get_token(ST.QualifierOperator, '.'),
                                get_token(T.Name, 'z'),
                            ]),
                            get_token(T.Whitespace, ' '),
                            get_token(ST.ComparisonOperator, '='),
                            get_token(T.Whitespace, ' '),
                            TokenGroup(ttype=ST.Identifier, token_list=[
                                get_token(ST.QualifierName, 'xyz'),
                                get_token(ST.QualifierOperator, '.'),
                                get_token(T.Name, 'z'),
                                get_token(T.Whitespace, ' '),
                                get_token(T.Comment.Single,
                                          '-- comments in between\n')
                            ]),
                        ]),
                    ]),
                ]),

                get_token(T.Whitespace, ' '),

                TokenGroup(ttype=ST.WhereClause, token_list=[
                    get_token(T.Keyword, 'WHERE'),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.Comparison, token_list=[
                        TokenGroup(ttype=ST.Identifier, token_list=[
                            get_token(ST.QualifierName, 'xyz'),
                            get_token(ST.QualifierOperator, '.'),
                            get_token(T.Name, 'x'),
                        ]),
                        get_token(T.Whitespace, ' '),
                        get_token(ST.ComparisonOperator, '>='),
                        get_token(T.Whitespace, ' '),
                        get_token(T.Number.Float, '20.5'),
                    ]),
                    get_token(T.Whitespace, ' '),
                    get_token(ST.LogicalOperator, 'AND'),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.In, token_list=[
                        TokenGroup(ttype=ST.Identifier, token_list=[
                            get_token(ST.QualifierName, 'abc'),
                            get_token(ST.QualifierOperator, '.'),
                            get_token(T.Name, 'p'),
                        ]),
                        get_token(T.Whitespace, ' '),
                        get_token(T.Keyword, 'IN'),
                        get_token(T.Whitespace, ' '),
                        TokenGroup(ttype=ST.SubQuery, token_list=[
                            get_token(T.Punctuation, '('),
                            TokenGroup(ttype=ST.SelectClause, token_list=[
                                get_token(T.Keyword, 'SELECT'),
                                get_token(T.Whitespace, ' '),
                                TokenGroup(ttype=ST.Identifier, token_list=[
                                    get_token(T.Name, 'j'),
                                ]),
                            ]),
                            get_token(T.Whitespace, ' '),
                            TokenGroup(ttype=ST.FromClause, token_list=[
                                get_token(T.Keyword, 'FROM'),
                                get_token(T.Whitespace, ' '),
                                TokenGroup(ttype=ST.Identifier, token_list=[
                                    get_token(T.Name, 'where_in_table'),
                                ]),
                            ]),
                            get_token(T.Punctuation, ')'),
                        ]),
                    ]),
                ]),

                get_token(T.Whitespace, ' '),

                TokenGroup(ttype=ST.GroupByClause, token_list=[
                    get_token(T.Keyword, 'GROUP'),
                    get_token(T.Whitespace, ' '),
                    get_token(T.Keyword, 'BY'),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.Identifier, token_list=[
                        get_token(ST.QualifierName, 'abc'),
                        get_token(ST.QualifierOperator, '.'),
                        get_token(T.Name, 'c'),
                    ]),
                ]),

                get_token(T.Punctuation, ';'),
            ]),
        ]
        i = 0
        print('--')
        print(sql_text)
        print('--')
        for x in p.parse(sql_text):
            _token_list_tracing_helper(x, exp_stmt[i])
            i += 1
        assert i == len(exp_stmt)
        print('')

    def test_005_group_by_and_having_and_order_by(self):
        p = PostgresParser()
        sql_text = '''
        select abc.c,
               count(xyz.*) total_count
        from abc join xyz
        on abc.z = xyz.z -- comments in between
        where xyz.x >= 20.5
        group by abc.c
        having count(xyz.*) > 500
        order by abc.c;
        '''
        exp_stmt = [
            PostgresSqlStatement(ttype=ST.Select, token_list=[
                TokenGroup(ttype=ST.SelectClause, token_list=[
                    get_token(T.Keyword, 'SELECT'),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.Identifier, token_list=[
                        get_token(ST.QualifierName, 'abc'),
                        get_token(ST.QualifierOperator, '.'),
                        get_token(T.Name, 'c'),
                    ]),
                    get_token(T.Punctuation, ','),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.Function, token_list=[
                        get_token(T.Name, 'count'),
                        TokenGroup(ttype=ST.ArgumentList, token_list=[
                            get_token(T.Punctuation, '('),
                            TokenGroup(ttype=ST.Identifier, token_list=[
                                get_token(ST.QualifierName, 'xyz'),
                                get_token(ST.QualifierOperator, '.'),
                                get_token(ST.AllColumnsIdentifier, '*'),
                            ]),
                            get_token(T.Punctuation, ')')
                        ]),
                        get_token(T.Whitespace, ' '),
                        get_token(ST.AliasName, 'total_count'),
                    ]),
                ]),

                get_token(T.Whitespace, ' '),

                TokenGroup(ttype=ST.FromClause, token_list=[
                    get_token(T.Keyword, 'FROM'),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.Identifier, token_list=[
                        get_token(T.Name, 'abc'),
                    ]),
                    get_token(T.Whitespace, ' '),
                    get_token(T.Keyword, 'JOIN'),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.Identifier, token_list=[
                        get_token(T.Name, 'xyz'),
                    ]),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.JoinOnClause, token_list=[
                        get_token(T.Keyword, 'ON'),
                        get_token(T.Whitespace, ' '),
                        TokenGroup(ttype=ST.Comparison, token_list=[
                            TokenGroup(ttype=ST.Identifier, token_list=[
                                get_token(ST.QualifierName, 'abc'),
                                get_token(ST.QualifierOperator, '.'),
                                get_token(T.Name, 'z'),
                            ]),
                            get_token(T.Whitespace, ' '),
                            get_token(ST.ComparisonOperator, '='),
                            get_token(T.Whitespace, ' '),
                            TokenGroup(ttype=ST.Identifier, token_list=[
                                get_token(ST.QualifierName, 'xyz'),
                                get_token(ST.QualifierOperator, '.'),
                                get_token(T.Name, 'z'),
                                get_token(T.Whitespace, ' '),
                                get_token(T.Comment.Single,
                                          '-- comments in between\n')
                            ]),
                        ]),
                    ]),
                ]),

                get_token(T.Whitespace, ' '),

                TokenGroup(ttype=ST.WhereClause, token_list=[
                    get_token(T.Keyword, 'WHERE'),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.Comparison, token_list=[
                        TokenGroup(ttype=ST.Identifier, token_list=[
                            get_token(ST.QualifierName, 'xyz'),
                            get_token(ST.QualifierOperator, '.'),
                            get_token(T.Name, 'x'),
                        ]),
                        get_token(T.Whitespace, ' '),
                        get_token(ST.ComparisonOperator, '>='),
                        get_token(T.Whitespace, ' '),
                        get_token(T.Number.Float, '20.5'),
                    ]),
                ]),

                get_token(T.Whitespace, ' '),

                TokenGroup(ttype=ST.GroupByClause, token_list=[
                    get_token(T.Keyword, 'GROUP'),
                    get_token(T.Whitespace, ' '),
                    get_token(T.Keyword, 'BY'),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.Identifier, token_list=[
                        get_token(ST.QualifierName, 'abc'),
                        get_token(ST.QualifierOperator, '.'),
                        get_token(T.Name, 'c'),
                    ]),
                ]),

                get_token(T.Whitespace, ' '),

                TokenGroup(ttype=ST.HavingClause, token_list=[
                    get_token(T.Keyword, 'HAVING'),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.Comparison, token_list=[
                        TokenGroup(ttype=ST.Function, token_list=[
                            get_token(T.Name, 'count'),
                            TokenGroup(ttype=ST.ArgumentList, token_list=[
                                get_token(T.Punctuation, '('),
                                TokenGroup(ttype=ST.Identifier, token_list=[
                                    get_token(ST.QualifierName, 'xyz'),
                                    get_token(ST.QualifierOperator, '.'),
                                    get_token(ST.AllColumnsIdentifier, '*'),
                                ]),
                                get_token(T.Punctuation, ')')
                            ]),
                        ]),
                        get_token(T.Whitespace, ' '),
                        get_token(ST.ComparisonOperator, '>'),
                        get_token(T.Whitespace, ' '),
                        get_token(T.Number.Integer, '500'),
                    ]),
                ]),

                get_token(T.Whitespace, ' '),

                TokenGroup(ttype=ST.OrderByClause, token_list=[
                    get_token(T.Keyword, 'ORDER'),
                    get_token(T.Whitespace, ' '),
                    get_token(T.Keyword, 'BY'),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.Identifier, token_list=[
                        get_token(ST.QualifierName, 'abc'),
                        get_token(ST.QualifierOperator, '.'),
                        get_token(T.Name, 'c'),
                    ]),
                ]),

                get_token(T.Punctuation, ';'),
            ]),
        ]
        i = 0
        print('--')
        print(sql_text)
        print('--')
        for x in p.parse(sql_text):
            _token_list_tracing_helper(x, exp_stmt[i])
            i += 1
        assert i == len(exp_stmt)
        print('')

    def test_006_between_and_like(self):
        p = PostgresParser()
        sql_text = '''
            select a, b
            from abc
            where b between 10 and 20
            and a like "%PeeDi_";
            '''
        exp_stmt = [
            PostgresSqlStatement(ttype=ST.Select, token_list=[
                TokenGroup(ttype=ST.SelectClause, token_list=[
                    get_token(T.Keyword, 'SELECT'),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.Identifier, token_list=[
                        get_token(T.Name, 'a'),
                    ]),
                    get_token(T.Punctuation, ','),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.Identifier, token_list=[
                        get_token(T.Name, 'b'),
                    ]),
                ]),

                get_token(T.Whitespace, ' '),

                TokenGroup(ttype=ST.FromClause, token_list=[
                    get_token(T.Keyword, 'FROM'),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.Identifier, token_list=[
                        get_token(T.Name, 'abc'),
                    ]),
                ]),

                get_token(T.Whitespace, ' '),

                TokenGroup(ttype=ST.WhereClause, token_list=[
                    get_token(T.Keyword, 'WHERE'),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.Between, token_list=[
                        TokenGroup(ttype=ST.Identifier, token_list=[
                            get_token(T.Name, 'b'),
                        ]),
                        get_token(T.Whitespace, ' '),
                        get_token(T.Keyword, 'BETWEEN'),
                        get_token(T.Whitespace, ' '),
                        get_token(T.Number.Integer, '10'),
                        get_token(T.Whitespace, ' '),
                        get_token(ST.LogicalOperator, 'AND'),
                        get_token(T.Whitespace, ' '),
                        get_token(T.Number.Integer, '20'),
                    ]),
                    get_token(T.Whitespace, ' '),
                    get_token(ST.LogicalOperator, 'AND'),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.Like, token_list=[
                        TokenGroup(ttype=ST.Identifier, token_list=[
                            get_token(T.Name, 'a'),
                        ]),
                        get_token(T.Whitespace, ' '),
                        get_token(T.Keyword, 'LIKE'),
                        get_token(T.Whitespace, ' '),
                        get_token(T.String, '"%PeeDi_"'),
                    ]),
                ]),

                get_token(T.Punctuation, ';'),
            ]),
        ]
        i = 0
        print('--')
        print(sql_text)
        print('--')
        for x in p.parse(sql_text):
            _token_list_tracing_helper(x, exp_stmt[i])
            i += 1
        assert i == len(exp_stmt)
        print('')

    def test_007_in_collection(self):
        p = PostgresParser()
        sql_text = '''
            select a, b, c
            from abc
            where c in (select q from qset)
            and b in (10, 20, 30, 40)
            and a in ("tap", "map");
            '''
        exp_stmt = [
            PostgresSqlStatement(ttype=ST.Select, token_list=[
                TokenGroup(ttype=ST.SelectClause, token_list=[
                    get_token(T.Keyword, 'SELECT'),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.Identifier, token_list=[
                        get_token(T.Name, 'a'),
                    ]),
                    get_token(T.Punctuation, ','),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.Identifier, token_list=[
                        get_token(T.Name, 'b'),
                    ]),
                    get_token(T.Punctuation, ','),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.Identifier, token_list=[
                        get_token(T.Name, 'c'),
                    ]),
                ]),

                get_token(T.Whitespace, ' '),

                TokenGroup(ttype=ST.FromClause, token_list=[
                    get_token(T.Keyword, 'FROM'),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.Identifier, token_list=[
                        get_token(T.Name, 'abc'),
                    ]),
                ]),

                get_token(T.Whitespace, ' '),

                TokenGroup(ttype=ST.WhereClause, token_list=[
                    get_token(T.Keyword, 'WHERE'),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.In, token_list=[
                        TokenGroup(ttype=ST.Identifier, token_list=[
                            get_token(T.Name, 'c'),
                        ]),
                        get_token(T.Whitespace, ' '),
                        get_token(T.Keyword, 'IN'),
                        get_token(T.Whitespace, ' '),
                        TokenGroup(ttype=ST.SubQuery, token_list=[
                            get_token(T.Punctuation, '('),
                            TokenGroup(ttype=ST.SelectClause, token_list=[
                                get_token(T.Keyword, 'SELECT'),
                                get_token(T.Whitespace, ' '),
                                TokenGroup(ttype=ST.Identifier, token_list=[
                                    get_token(T.Name, 'q'),
                                ]),
                            ]),
                            get_token(T.Whitespace, ' '),
                            TokenGroup(ttype=ST.FromClause, token_list=[
                                get_token(T.Keyword, 'FROM'),
                                get_token(T.Whitespace, ' '),
                                TokenGroup(ttype=ST.Identifier, token_list=[
                                    get_token(T.Name, 'qset'),
                                ]),
                            ]),
                            get_token(T.Punctuation, ')'),
                        ]),
                    ]),
                    get_token(T.Whitespace, ' '),
                    get_token(ST.LogicalOperator, 'AND'),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.In, token_list=[
                        TokenGroup(ttype=ST.Identifier, token_list=[
                            get_token(T.Name, 'b'),
                        ]),
                        get_token(T.Whitespace, ' '),
                        get_token(T.Keyword, 'IN'),
                        get_token(T.Whitespace, ' '),
                        TokenGroup(ttype=ST.CollectionSet, token_list=[
                            get_token(T.Punctuation, '('),
                            get_token(T.Number.Integer, '10'),
                            get_token(T.Punctuation, ','),
                            get_token(T.Whitespace, ' '),
                            get_token(T.Number.Integer, '20'),
                            get_token(T.Punctuation, ','),
                            get_token(T.Whitespace, ' '),
                            get_token(T.Number.Integer, '30'),
                            get_token(T.Punctuation, ','),
                            get_token(T.Whitespace, ' '),
                            get_token(T.Number.Integer, '40'),
                            get_token(T.Punctuation, ')'),
                        ]),
                    ]),
                    get_token(T.Whitespace, ' '),
                    get_token(ST.LogicalOperator, 'AND'),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.In, token_list=[
                        TokenGroup(ttype=ST.Identifier, token_list=[
                            get_token(T.Name, 'a'),
                        ]),
                        get_token(T.Whitespace, ' '),
                        get_token(T.Keyword, 'IN'),
                        get_token(T.Whitespace, ' '),
                        TokenGroup(ttype=ST.CollectionSet, token_list=[
                            get_token(T.Punctuation, '('),
                            get_token(T.String, '"tap"'),
                            get_token(T.Punctuation, ','),
                            get_token(T.Whitespace, ' '),
                            get_token(T.String, '"map"'),
                            get_token(T.Punctuation, ')'),
                        ]),
                    ]),
                ]),

                get_token(T.Punctuation, ';'),
            ]),
        ]
        i = 0
        print('--')
        print(sql_text)
        print('--')
        for x in p.parse(sql_text):
            _token_list_tracing_helper(x, exp_stmt[i])
            i += 1
        assert i == len(exp_stmt)
        print('')

    def test_008_distinct_and_select_into_and_limit(self):
        p = PostgresParser()
        sql_text = '''
            select distinct a, b, c
            into xyz
            from abc
            limit 100;
            '''
        exp_stmt = [
            PostgresSqlStatement(ttype=ST.SelectInto, token_list=[
                TokenGroup(ttype=ST.SelectClause, token_list=[
                    get_token(T.Keyword, 'SELECT'),
                    get_token(T.Whitespace, ' '),
                    get_token(T.Keyword, 'DISTINCT'),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.Identifier, token_list=[
                        get_token(T.Name, 'a'),
                    ]),
                    get_token(T.Punctuation, ','),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.Identifier, token_list=[
                        get_token(T.Name, 'b'),
                    ]),
                    get_token(T.Punctuation, ','),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.Identifier, token_list=[
                        get_token(T.Name, 'c'),
                    ]),
                ]),

                get_token(T.Whitespace, ' '),

                TokenGroup(ttype=ST.SelectIntoClause, token_list=[
                    get_token(T.Keyword, 'INTO'),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.Identifier, token_list=[
                        get_token(T.Name, 'xyz'),
                    ]),
                ]),

                get_token(T.Whitespace, ' '),

                TokenGroup(ttype=ST.FromClause, token_list=[
                    get_token(T.Keyword, 'FROM'),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.Identifier, token_list=[
                        get_token(T.Name, 'abc'),
                    ]),
                ]),

                get_token(T.Whitespace, ' '),

                TokenGroup(ttype=PT.LimitClause, token_list=[
                    get_token(T.Keyword, 'LIMIT'),
                    get_token(T.Whitespace, ' '),
                    get_token(T.Number.Integer, '100'),
                ]),

                get_token(T.Punctuation, ';'),
            ]),
        ]
        i = 0
        print('--')
        print(sql_text)
        print('--')
        for x in p.parse(sql_text):
            _token_list_tracing_helper(x, exp_stmt[i])
            i += 1
        assert i == len(exp_stmt)
        print('')

    def test_009_not_condition(self):
        p = PostgresParser()
        sql_text = '''
        select abc.c,
               count(xyz.*) total_count,
               sum(abc.d) some_sum
        from abc join xyz
        on abc.z = xyz.z or xyz.a not in (abc.c,abc.d)
        where xyz.x >= 20.5
        or xyz.y not like '%NOT_LIKE%'
        group by abc.c
        having count(xyz.*) > 500
        or sum(abc.d) not between 2000 and 50000
        order by abc.c;
        '''
        exp_stmt = [
            PostgresSqlStatement(ttype=ST.Select, token_list=[
                TokenGroup(ttype=ST.SelectClause, token_list=[
                    get_token(T.Keyword, 'SELECT'),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.Identifier, token_list=[
                        get_token(ST.QualifierName, 'abc'),
                        get_token(ST.QualifierOperator, '.'),
                        get_token(T.Name, 'c'),
                    ]),
                    get_token(T.Punctuation, ','),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.Function, token_list=[
                        get_token(T.Name, 'count'),
                        TokenGroup(ttype=ST.ArgumentList, token_list=[
                            get_token(T.Punctuation, '('),
                            TokenGroup(ttype=ST.Identifier, token_list=[
                                get_token(ST.QualifierName, 'xyz'),
                                get_token(ST.QualifierOperator, '.'),
                                get_token(ST.AllColumnsIdentifier, '*'),
                            ]),
                            get_token(T.Punctuation, ')')
                        ]),
                        get_token(T.Whitespace, ' '),
                        get_token(ST.AliasName, 'total_count'),
                    ]),
                    get_token(T.Punctuation, ','),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.Function, token_list=[
                        get_token(T.Name, 'sum'),
                        TokenGroup(ttype=ST.ArgumentList, token_list=[
                            get_token(T.Punctuation, '('),
                            TokenGroup(ttype=ST.Identifier, token_list=[
                                get_token(ST.QualifierName, 'abc'),
                                get_token(ST.QualifierOperator, '.'),
                                get_token(T.Name, 'd'),
                            ]),
                            get_token(T.Punctuation, ')')
                        ]),
                        get_token(T.Whitespace, ' '),
                        get_token(ST.AliasName, 'some_sum'),
                    ]),
                ]),

                get_token(T.Whitespace, ' '),

                TokenGroup(ttype=ST.FromClause, token_list=[
                    get_token(T.Keyword, 'FROM'),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.Identifier, token_list=[
                        get_token(T.Name, 'abc'),
                    ]),
                    get_token(T.Whitespace, ' '),
                    get_token(T.Keyword, 'JOIN'),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.Identifier, token_list=[
                        get_token(T.Name, 'xyz'),
                    ]),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.JoinOnClause, token_list=[
                        get_token(T.Keyword, 'ON'),
                        get_token(T.Whitespace, ' '),
                        TokenGroup(ttype=ST.Comparison, token_list=[
                            TokenGroup(ttype=ST.Identifier, token_list=[
                                get_token(ST.QualifierName, 'abc'),
                                get_token(ST.QualifierOperator, '.'),
                                get_token(T.Name, 'z'),
                            ]),
                            get_token(T.Whitespace, ' '),
                            get_token(ST.ComparisonOperator, '='),
                            get_token(T.Whitespace, ' '),
                            TokenGroup(ttype=ST.Identifier, token_list=[
                                get_token(ST.QualifierName, 'xyz'),
                                get_token(ST.QualifierOperator, '.'),
                                get_token(T.Name, 'z'),
                            ]),
                        ]),
                        get_token(T.Whitespace, ' '),
                        get_token(ST.LogicalOperator, 'OR'),
                        get_token(T.Whitespace, ' '),
                        TokenGroup(ttype=ST.NotIn, token_list=[
                            TokenGroup(ttype=ST.Identifier, token_list=[
                                get_token(ST.QualifierName, 'xyz'),
                                get_token(ST.QualifierOperator, '.'),
                                get_token(T.Name, 'a'),
                            ]),
                            get_token(T.Whitespace, ' '),
                            get_token(ST.LogicalOperator, 'NOT'),
                            get_token(T.Whitespace, ' '),
                            get_token(T.Keyword, 'IN'),
                            get_token(T.Whitespace, ' '),
                            TokenGroup(ttype=ST.CollectionSet, token_list=[
                                get_token(T.Punctuation, '('),
                                TokenGroup(ttype=ST.Identifier, token_list=[
                                    get_token(ST.QualifierName, 'abc'),
                                    get_token(ST.QualifierOperator, '.'),
                                    get_token(T.Name, 'c'),
                                ]),
                                get_token(T.Punctuation, ','),
                                TokenGroup(ttype=ST.Identifier, token_list=[
                                    get_token(ST.QualifierName, 'abc'),
                                    get_token(ST.QualifierOperator, '.'),
                                    get_token(T.Name, 'd'),
                                ]),
                                get_token(T.Punctuation, ')'),
                            ]),
                        ]),
                    ]),
                ]),

                get_token(T.Whitespace, ' '),

                TokenGroup(ttype=ST.WhereClause, token_list=[
                    get_token(T.Keyword, 'WHERE'),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.Comparison, token_list=[
                        TokenGroup(ttype=ST.Identifier, token_list=[
                            get_token(ST.QualifierName, 'xyz'),
                            get_token(ST.QualifierOperator, '.'),
                            get_token(T.Name, 'x'),
                        ]),
                        get_token(T.Whitespace, ' '),
                        get_token(ST.ComparisonOperator, '>='),
                        get_token(T.Whitespace, ' '),
                        get_token(T.Number.Float, '20.5'),
                    ]),
                    get_token(T.Whitespace, ' '),
                    get_token(ST.LogicalOperator, 'OR'),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.NotLike, token_list=[
                        TokenGroup(ttype=ST.Identifier, token_list=[
                            get_token(ST.QualifierName, 'xyz'),
                            get_token(ST.QualifierOperator, '.'),
                            get_token(T.Name, 'y'),
                        ]),
                        get_token(T.Whitespace, ' '),
                        get_token(ST.LogicalOperator, 'NOT'),
                        get_token(T.Whitespace, ' '),
                        get_token(T.Keyword, 'LIKE'),
                        get_token(T.Whitespace, ' '),
                        get_token(T.String, "'%NOT_LIKE%'"),
                    ]),
                ]),

                get_token(T.Whitespace, ' '),

                TokenGroup(ttype=ST.GroupByClause, token_list=[
                    get_token(T.Keyword, 'GROUP'),
                    get_token(T.Whitespace, ' '),
                    get_token(T.Keyword, 'BY'),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.Identifier, token_list=[
                        get_token(ST.QualifierName, 'abc'),
                        get_token(ST.QualifierOperator, '.'),
                        get_token(T.Name, 'c'),
                    ]),
                ]),

                get_token(T.Whitespace, ' '),

                TokenGroup(ttype=ST.HavingClause, token_list=[
                    get_token(T.Keyword, 'HAVING'),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.Comparison, token_list=[
                        TokenGroup(ttype=ST.Function, token_list=[
                            get_token(T.Name, 'count'),
                            TokenGroup(ttype=ST.ArgumentList, token_list=[
                                get_token(T.Punctuation, '('),
                                TokenGroup(ttype=ST.Identifier, token_list=[
                                    get_token(ST.QualifierName, 'xyz'),
                                    get_token(ST.QualifierOperator, '.'),
                                    get_token(ST.AllColumnsIdentifier, '*'),
                                ]),
                                get_token(T.Punctuation, ')')
                            ]),
                        ]),
                        get_token(T.Whitespace, ' '),
                        get_token(ST.ComparisonOperator, '>'),
                        get_token(T.Whitespace, ' '),
                        get_token(T.Number.Integer, '500'),
                    ]),
                    get_token(T.Whitespace, ' '),
                    get_token(ST.LogicalOperator, 'OR'),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.NotBetween, token_list=[
                        TokenGroup(ttype=ST.Function, token_list=[
                            get_token(T.Name, 'sum'),
                            TokenGroup(ttype=ST.ArgumentList, token_list=[
                                get_token(T.Punctuation, '('),
                                TokenGroup(ttype=ST.Identifier, token_list=[
                                    get_token(ST.QualifierName, 'abc'),
                                    get_token(ST.QualifierOperator, '.'),
                                    get_token(T.Name, 'd'),
                                ]),
                                get_token(T.Punctuation, ')')
                            ]),
                        ]),
                        get_token(T.Whitespace, ' '),
                        get_token(ST.LogicalOperator, 'NOT'),
                        get_token(T.Whitespace, ' '),
                        get_token(T.Keyword, 'BETWEEN'),
                        get_token(T.Whitespace, ' '),
                        get_token(T.Number.Integer, '2000'),
                        get_token(T.Whitespace, ' '),
                        get_token(ST.LogicalOperator, 'AND'),
                        get_token(T.Whitespace, ' '),
                        get_token(T.Number.Integer, '50000'),
                    ]),
                ]),

                get_token(T.Whitespace, ' '),

                TokenGroup(ttype=ST.OrderByClause, token_list=[
                    get_token(T.Keyword, 'ORDER'),
                    get_token(T.Whitespace, ' '),
                    get_token(T.Keyword, 'BY'),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.Identifier, token_list=[
                        get_token(ST.QualifierName, 'abc'),
                        get_token(ST.QualifierOperator, '.'),
                        get_token(T.Name, 'c'),
                    ]),
                ]),

                get_token(T.Punctuation, ';'),
            ]),
        ]
        i = 0
        print('--')
        print(sql_text)
        print('--')
        for x in p.parse(sql_text):
            _token_list_tracing_helper(x, exp_stmt[i])
            i += 1
        assert i == len(exp_stmt)
        print('')

    def test_010_expression(self):
        p = PostgresParser()
        sql_text = '''
        select 10 + abc.x computed_field_1,
            abc.c*xyz.d+unambiguous_column-1 as computed_field_2,
            (unambiguous_column-1) as computed_field_3,
            (2*(1-2)) computed_field_4,
            100 % 4 computed_field_5,
            2 as constant_value ,
            3,
            (abc.p % 100),
            4 other_constant_value
        from abc join xyz
        on abc.z = xyz.z
        where ((abc.m - 10)*500>10000) and 2>1;
        '''
        exp_stmt = [
            PostgresSqlStatement(ttype=ST.Select, token_list=[
                TokenGroup(ttype=ST.SelectClause, token_list=[
                    get_token(T.Keyword, 'SELECT'),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.ComputedIdentifier, token_list=[
                        get_token(T.Number.Integer, '10'),
                        get_token(T.Whitespace, ' '),
                        get_token(T.Operator, '+'),
                        get_token(T.Whitespace, ' '),
                        TokenGroup(ttype=ST.Identifier, token_list=[
                            get_token(ST.QualifierName, 'abc'),
                            get_token(ST.QualifierOperator, '.'),
                            get_token(T.Name, 'x'),
                        ]),
                        get_token(T.Whitespace, ' '),
                        get_token(ST.AliasName, 'computed_field_1'),
                    ]),
                    get_token(T.Punctuation, ','),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.ComputedIdentifier, token_list=[
                        TokenGroup(ttype=ST.Identifier, token_list=[
                            get_token(ST.QualifierName, 'abc'),
                            get_token(ST.QualifierOperator, '.'),
                            get_token(T.Name, 'c'),
                        ]),
                        get_token(T.Operator, '*'),
                        TokenGroup(ttype=ST.Identifier, token_list=[
                            get_token(ST.QualifierName, 'xyz'),
                            get_token(ST.QualifierOperator, '.'),
                            get_token(T.Name, 'd'),
                        ]),
                        get_token(T.Operator, '+'),
                        TokenGroup(ttype=ST.Identifier, token_list=[
                            get_token(T.Name, 'unambiguous_column'),
                        ]),
                        get_token(T.Operator, '-'),
                        get_token(T.Number.Integer, '1'),
                        get_token(T.Whitespace, ' '),
                        get_token(T.Keyword, 'AS'),
                        get_token(T.Whitespace, ' '),
                        get_token(ST.AliasName, 'computed_field_2'),
                    ]),
                    get_token(T.Punctuation, ','),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.ComputedIdentifier, token_list=[
                        TokenGroup(ttype=ST.RoundBracket, token_list=[
                            get_token(T.Punctuation, '('),
                            TokenGroup(ttype=ST.ComputedIdentifier, token_list=[
                                TokenGroup(ttype=ST.Identifier, token_list=[
                                    get_token(T.Name, 'unambiguous_column'),
                                ]),
                                get_token(T.Operator, '-'),
                                get_token(T.Number.Integer, '1'),
                            ]),
                            get_token(T.Punctuation, ')'),
                        ]),
                        get_token(T.Whitespace, ' '),
                        get_token(T.Keyword, 'AS'),
                        get_token(T.Whitespace, ' '),
                        get_token(ST.AliasName, 'computed_field_3'),
                    ]),
                    get_token(T.Punctuation, ','),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.ComputedIdentifier, token_list=[
                        TokenGroup(ttype=ST.RoundBracket, token_list=[
                            get_token(T.Punctuation, '('),
                            TokenGroup(ttype=ST.ComputedIdentifier, token_list=[
                                get_token(T.Number.Integer, '2'),
                                get_token(T.Operator, '*'),
                                TokenGroup(ttype=ST.RoundBracket, token_list=[
                                    get_token(T.Punctuation, '('),
                                    TokenGroup(ttype=ST.ComputedIdentifier, token_list=[
                                        get_token(T.Number.Integer, '1'),
                                        get_token(T.Operator, '-'),
                                        get_token(T.Number.Integer, '2'),
                                    ]),
                                    get_token(T.Punctuation, ')'),
                                ]),
                            ]),
                            get_token(T.Punctuation, ')'),
                        ]),
                        get_token(T.Whitespace, ' '),
                        get_token(ST.AliasName, 'computed_field_4'),
                    ]),
                    get_token(T.Punctuation, ','),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.ComputedIdentifier, token_list=[
                        get_token(T.Number.Integer, '100'),
                        get_token(T.Whitespace, ' '),
                        get_token(T.Operator, '%'),
                        get_token(T.Whitespace, ' '),
                        get_token(T.Number.Integer, '4'),
                        get_token(T.Whitespace, ' '),
                        get_token(ST.AliasName, 'computed_field_5'),
                    ]),
                    get_token(T.Punctuation, ','),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.SelectConstantIdentifier, token_list=[
                        get_token(T.Number.Integer, '2'),
                        get_token(T.Whitespace, ' '),
                        get_token(T.Keyword, 'AS'),
                        get_token(T.Whitespace, ' '),
                        get_token(ST.AliasName, 'constant_value'),
                    ]),
                    get_token(T.Whitespace, ' '),
                    get_token(T.Punctuation, ','),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.SelectConstantIdentifier, token_list=[
                        get_token(T.Number.Integer, '3'),
                    ]),
                    get_token(T.Punctuation, ','),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.ComputedIdentifier, token_list=[
                        TokenGroup(ttype=ST.RoundBracket, token_list=[
                            get_token(T.Punctuation, '('),
                            TokenGroup(ttype=ST.ComputedIdentifier, token_list=[
                                TokenGroup(ttype=ST.Identifier, token_list=[
                                    get_token(ST.QualifierName, 'abc'),
                                    get_token(ST.QualifierOperator, '.'),
                                    get_token(T.Name, 'p'),
                                ]),
                                get_token(T.Whitespace, ' '),
                                get_token(T.Operator, '%'),
                                get_token(T.Whitespace, ' '),
                                get_token(T.Number.Integer, '100'),
                            ]),
                            get_token(T.Punctuation, ')'),
                        ]),
                    ]),
                    get_token(T.Punctuation, ','),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.SelectConstantIdentifier, token_list=[
                        get_token(T.Number.Integer, '4'),
                        get_token(T.Whitespace, ' '),
                        get_token(ST.AliasName, 'other_constant_value'),
                    ]),
                ]),

                get_token(T.Whitespace, ' '),

                TokenGroup(ttype=ST.FromClause, token_list=[
                    get_token(T.Keyword, 'FROM'),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.Identifier, token_list=[
                        get_token(T.Name, 'abc'),
                    ]),
                    get_token(T.Whitespace, ' '),
                    get_token(T.Keyword, 'JOIN'),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.Identifier, token_list=[
                        get_token(T.Name, 'xyz'),
                    ]),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.JoinOnClause, token_list=[
                        get_token(T.Keyword, 'ON'),
                        get_token(T.Whitespace, ' '),
                        TokenGroup(ttype=ST.Comparison, token_list=[
                            TokenGroup(ttype=ST.Identifier, token_list=[
                                get_token(ST.QualifierName, 'abc'),
                                get_token(ST.QualifierOperator, '.'),
                                get_token(T.Name, 'z'),
                            ]),
                            get_token(T.Whitespace, ' '),
                            get_token(ST.ComparisonOperator, '='),
                            get_token(T.Whitespace, ' '),
                            TokenGroup(ttype=ST.Identifier, token_list=[
                                get_token(ST.QualifierName, 'xyz'),
                                get_token(ST.QualifierOperator, '.'),
                                get_token(T.Name, 'z'),
                            ]),
                        ]),
                    ]),
                ]),

                get_token(T.Whitespace, ' '),

                TokenGroup(ttype=ST.WhereClause, token_list=[
                    get_token(T.Keyword, 'WHERE'),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.ConditionGroup, token_list=[
                        get_token(T.Punctuation, '('),
                        TokenGroup(ttype=ST.Comparison, token_list=[
                            TokenGroup(ttype=ST.ComputedIdentifier, token_list=[
                                TokenGroup(ttype=ST.RoundBracket, token_list=[
                                    get_token(T.Punctuation, '('),
                                    TokenGroup(ttype=ST.ComputedIdentifier, token_list=[
                                        TokenGroup(ttype=ST.Identifier, token_list=[
                                            get_token(ST.QualifierName, 'abc'),
                                            get_token(
                                                ST.QualifierOperator, '.'),
                                            get_token(T.Name, 'm'),
                                        ]),
                                        get_token(T.Whitespace, ' '),
                                        get_token(T.Operator, '-'),
                                        get_token(T.Whitespace, ' '),
                                        get_token(T.Number.Integer, '10'),
                                    ]),
                                    get_token(T.Punctuation, ')'),
                                ]),
                                # get_token(T.Whitespace, ' '),
                                get_token(T.Operator, '*'),
                                # get_token(T.Whitespace, ' '),
                                get_token(T.Number.Integer, '500'),
                            ]),
                            # get_token(T.Whitespace, ' '),
                            get_token(ST.ComparisonOperator, '>'),
                            # get_token(T.Whitespace, ' '),
                            get_token(T.Number.Integer, '10000'),
                        ]),
                        get_token(T.Punctuation, ')'),
                    ]),
                    get_token(T.Whitespace, ' '),
                    get_token(ST.LogicalOperator, 'AND'),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.Comparison, token_list=[
                        get_token(T.Number.Integer, '2'),
                        get_token(ST.ComparisonOperator, '>'),
                        get_token(T.Number.Integer, '1'),
                    ]),
                ]),

                get_token(T.Punctuation, ';'),
            ]),
        ]
        i = 0
        print('--')
        print(sql_text)
        print('--')
        for x in p.parse(sql_text):
            _token_list_tracing_helper(x, exp_stmt[i])
            i += 1
        assert i == len(exp_stmt)
        print('')

    def test_011_case(self):
        p = PostgresParser()
        sql_text = '''
        select case col1 
                when 0 then 'ZERO'
                when 1, 2 then 'ONE_OR_TWO'
                else 'MANY'
               end num_to_text,
               case when col2 > 500 then 500
                    when col2 > 200 then 200
                    else 0
               end as credit
        from sometable
        where case when x <> 0 then y/x > 1.5 else false end;
        '''
        exp_stmt = [
            PostgresSqlStatement(ttype=ST.Select, token_list=[
                TokenGroup(ttype=ST.SelectClause, token_list=[
                    get_token(T.Keyword, 'SELECT'),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.CaseExpression, token_list=[
                        get_token(T.Keyword, 'CASE'),
                        get_token(T.Whitespace, ' '),
                        TokenGroup(ttype=ST.Identifier, token_list=[
                            get_token(T.Name, 'col1'),
                        ]),
                        get_token(T.Whitespace, ' '),
                        TokenGroup(ttype=ST.WhenExpression, token_list=[
                            get_token(T.Keyword, 'WHEN'),
                            get_token(T.Whitespace, ' '),
                            get_token(T.Number.Integer, '0'),
                            get_token(T.Whitespace, ' '),
                            TokenGroup(ttype=ST.ThenExpression, token_list=[
                                get_token(T.Keyword, 'THEN'),
                                get_token(T.Whitespace, ' '),
                                get_token(T.String, "'ZERO'"),
                            ]),
                        ]),
                        get_token(T.Whitespace, ' '),
                        TokenGroup(ttype=ST.WhenExpression, token_list=[
                            get_token(T.Keyword, 'WHEN'),
                            get_token(T.Whitespace, ' '),
                            get_token(T.Number.Integer, '1'),
                            get_token(T.Punctuation, ','),
                            get_token(T.Whitespace, ' '),
                            get_token(T.Number.Integer, '2'),
                            get_token(T.Whitespace, ' '),
                            TokenGroup(ttype=ST.ThenExpression, token_list=[
                                get_token(T.Keyword, 'THEN'),
                                get_token(T.Whitespace, ' '),
                                get_token(T.String, "'ONE_OR_TWO'"),
                            ]),
                        ]),
                        get_token(T.Whitespace, ' '),
                        TokenGroup(ttype=ST.ElseExpression, token_list=[
                            get_token(T.Keyword, 'ELSE'),
                            get_token(T.Whitespace, ' '),
                            get_token(T.String, "'MANY'"),
                        ]),
                        get_token(T.Whitespace, ' '),
                        get_token(T.Keyword, 'END'),
                        get_token(T.Whitespace, ' '),
                        get_token(ST.AliasName, 'num_to_text'),
                    ]),
                    get_token(T.Punctuation, ','),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.CaseExpression, token_list=[
                        get_token(T.Keyword, 'CASE'),
                        get_token(T.Whitespace, ' '),
                        TokenGroup(ttype=ST.WhenExpression, token_list=[
                            get_token(T.Keyword, 'WHEN'),
                            get_token(T.Whitespace, ' '),
                            TokenGroup(ttype=ST.Comparison, token_list=[
                                TokenGroup(ttype=ST.Identifier, token_list=[
                                    get_token(T.Name, 'col2'),
                                ]),
                                get_token(T.Whitespace, ' '),
                                get_token(ST.ComparisonOperator, '>'),
                                get_token(T.Whitespace, ' '),
                                get_token(T.Number.Integer, '500'),
                            ]),
                            get_token(T.Whitespace, ' '),
                            TokenGroup(ttype=ST.ThenExpression, token_list=[
                                get_token(T.Keyword, 'THEN'),
                                get_token(T.Whitespace, ' '),
                                get_token(T.Number.Integer, '500'),
                            ]),
                        ]),
                        get_token(T.Whitespace, ' '),
                        TokenGroup(ttype=ST.WhenExpression, token_list=[
                            get_token(T.Keyword, 'WHEN'),
                            get_token(T.Whitespace, ' '),
                            TokenGroup(ttype=ST.Comparison, token_list=[
                                TokenGroup(ttype=ST.Identifier, token_list=[
                                    get_token(T.Name, 'col2'),
                                ]),
                                get_token(T.Whitespace, ' '),
                                get_token(ST.ComparisonOperator, '>'),
                                get_token(T.Whitespace, ' '),
                                get_token(T.Number.Integer, '200'),
                            ]),
                            get_token(T.Whitespace, ' '),
                            TokenGroup(ttype=ST.ThenExpression, token_list=[
                                get_token(T.Keyword, 'THEN'),
                                get_token(T.Whitespace, ' '),
                                get_token(T.Number.Integer, '200'),
                            ]),
                        ]),
                        get_token(T.Whitespace, ' '),
                        TokenGroup(ttype=ST.ElseExpression, token_list=[
                            get_token(T.Keyword, 'ELSE'),
                            get_token(T.Whitespace, ' '),
                            get_token(T.Number.Integer, '0'),
                        ]),
                        get_token(T.Whitespace, ' '),
                        get_token(T.Keyword, 'END'),
                        get_token(T.Whitespace, ' '),
                        get_token(T.Keyword, 'AS'),
                        get_token(T.Whitespace, ' '),
                        get_token(ST.AliasName, 'credit'),
                    ]),
                ]),

                get_token(T.Whitespace, ' '),

                TokenGroup(ttype=ST.FromClause, token_list=[
                    get_token(T.Keyword, 'FROM'),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.Identifier, token_list=[
                        get_token(T.Name, 'sometable'),
                    ]),
                ]),

                get_token(T.Whitespace, ' '),

                TokenGroup(ttype=ST.WhereClause, token_list=[
                    get_token(T.Keyword, 'WHERE'),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.CaseExpression, token_list=[
                        get_token(T.Keyword, 'CASE'),
                        get_token(T.Whitespace, ' '),
                        TokenGroup(ttype=ST.WhenExpression, token_list=[
                            get_token(T.Keyword, 'WHEN'),
                            get_token(T.Whitespace, ' '),
                            TokenGroup(ttype=ST.Comparison, token_list=[
                                TokenGroup(ttype=ST.Identifier, token_list=[
                                    get_token(T.Name, 'x'),
                                ]),
                                get_token(T.Whitespace, ' '),
                                get_token(ST.ComparisonOperator, '<>'),
                                get_token(T.Whitespace, ' '),
                                get_token(T.Number.Integer, '0'),
                            ]),
                            get_token(T.Whitespace, ' '),
                            TokenGroup(ttype=ST.ThenExpression, token_list=[
                                get_token(T.Keyword, 'THEN'),
                                get_token(T.Whitespace, ' '),
                                TokenGroup(ttype=ST.Comparison, token_list=[
                                    TokenGroup(ttype=ST.ComputedIdentifier, token_list=[
                                        TokenGroup(ttype=ST.Identifier, token_list=[
                                            get_token(T.Name, 'y'),
                                        ]),
                                        get_token(T.Operator, '/'),
                                        TokenGroup(ttype=ST.Identifier, token_list=[
                                            get_token(T.Name, 'x'),
                                        ]),
                                    ]),
                                    get_token(T.Whitespace, ' '),
                                    get_token(ST.ComparisonOperator, '>'),
                                    get_token(T.Whitespace, ' '),
                                    get_token(T.Number.Float, '1.5'),
                                ]),
                            ]),
                        ]),
                        get_token(T.Whitespace, ' '),
                        TokenGroup(ttype=ST.ElseExpression, token_list=[
                            get_token(T.Keyword, 'ELSE'),
                            get_token(T.Whitespace, ' '),
                            get_token(T.Keyword, 'FALSE'),
                        ]),
                        get_token(T.Whitespace, ' '),
                        get_token(T.Keyword, 'END'),
                    ]),
                ]),
                get_token(T.Punctuation, ';'),
            ]),
        ]
        i = 0
        print('--')
        print(sql_text)
        print('--')
        for x in p.parse(sql_text):
            _token_list_tracing_helper(x, exp_stmt[i])
            i += 1
        assert i == len(exp_stmt)
        print('')
