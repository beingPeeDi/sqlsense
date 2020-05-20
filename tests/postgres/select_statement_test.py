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

        SELECT upper(a.c) AS c,   p.*
        FROM abc.a_table AS a JOIN long_table_name p
        ON a.z = p.z;
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

        SELECT upper(abc.c)   c,       xyz.*
        FROM abc JOIN (SELECT * FROM subtable) xyz
        ON abc.z = xyz.z;
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
        SELECT add_nums(abc.c, 5) AS c,       xyz.*
        FROM abc JOIN (SELECT * FROM subtable) AS xyz
        ON abc.z = xyz.z -- comments in between
        WHERE xyz.x >= 20.5
        AND abc.p IN (SELECT j FROM where_in_table);
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
        SELECT upper(abc.c) AS c,
               count(xyz.*) total_count
        FROM abc JOIN (SELECT * FROM subtable WHERE some_col IS NOT NULL) xyz
        ON abc.z = xyz.z -- comments in between
        WHERE xyz.x >= 20.5
        AND abc.p IN (SELECT j FROM where_in_table)
        GROUP BY abc.c;
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
        SELECT abc.c,
               count(xyz.*) total_count
        FROM abc JOIN xyz
        ON abc.z = xyz.z -- comments in between
        WHERE xyz.x >= 20.5
        GROUP BY abc.c
        HAVING count(xyz.*) > 500
        ORDER BY abc.c;
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
            SELECT a, b
            FROM abc
            WHERE b BETWEEN 10 AND 20
            AND a LIKE "%PeeDi_";
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
            SELECT a, b, c
            FROM abc
            WHERE c IN (SELECT q FROM qset)
            AND b IN (10, 20, 30, 40)
            AND a IN ("tap", "map");
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
            SELECT DISTINCT a, b, c
            INTO xyz
            FROM abc
            LIMIT 100;
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
        SELECT abc.c,
               count(xyz.*) total_count,
               sum(abc.d) some_sum
        FROM abc JOIN xyz
        ON abc.z = xyz.z OR xyz.a NOT IN (abc.c,abc.d)
        WHERE xyz.x >= 20.5
        OR xyz.y NOT LIKE '%NOT_LIKE%'
        GROUP BY abc.c
        HAVING count(xyz.*) > 500
        OR sum(abc.d) NOT BETWEEN 2000 AND 50000
        ORDER BY abc.c;
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
        SELECT 10 + abc.x computed_field_1,
            abc.c*xyz.d+unambiguous_column-1 AS computed_field_2,
            (unambiguous_column-1) AS computed_field_3,
            (2*(1-2)) computed_field_4,
            100 % 4 computed_field_5,
            2 AS constant_value ,
            3,
            (9),
            (abc.p % 100),
            4 other_constant_value
        FROM abc JOIN xyz
        ON abc.z = xyz.z
        WHERE ((abc.m - 10)*500>10000) AND 2>1;
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
                            get_token(T.Number.Integer, '9'),
                            get_token(T.Punctuation, ')'),
                        ]),
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
        SELECT CASE col1 
                WHEN 0 THEN 'ZERO'
                WHEN 1, 2 THEN 'ONE_OR_TWO'
                ELSE 'MANY'
               END num_to_text,
               CASE WHEN col2 > 500 THEN 500
                    WHEN col2 > 200 THEN CASE WHEN col2 > 400 THEN 400 
                                              ELSE 200 
                                         END
                    ELSE 0
               END AS credit
        FROM sometable
        WHERE CASE WHEN x <> 0 THEN y/x > 1.5 ELSE FALSE END;
        '''
        exp_stmt = [
            PostgresSqlStatement(ttype=ST.Select, token_list=[
                TokenGroup(ttype=ST.SelectClause, token_list=[
                    get_token(T.Keyword, 'SELECT'),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.ComputedIdentifier, token_list=[
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
                        ]),
                        get_token(T.Whitespace, ' '),
                        get_token(ST.AliasName, 'num_to_text'),
                    ]),
                    get_token(T.Punctuation, ','),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.ComputedIdentifier, token_list=[
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
                                                get_token(
                                                    ST.ComparisonOperator, '>'),
                                                get_token(T.Whitespace, ' '),
                                                get_token(
                                                    T.Number.Integer, '400'),
                                            ]),
                                            get_token(T.Whitespace, ' '),
                                            TokenGroup(ttype=ST.ThenExpression, token_list=[
                                                get_token(T.Keyword, 'THEN'),
                                                get_token(T.Whitespace, ' '),
                                                get_token(
                                                    T.Number.Integer, '400'),
                                            ]),
                                        ]),
                                        get_token(T.Whitespace, ' '),
                                        TokenGroup(ttype=ST.ElseExpression, token_list=[
                                            get_token(T.Keyword, 'ELSE'),
                                            get_token(T.Whitespace, ' '),
                                            get_token(T.Number.Integer, '200'),
                                        ]),
                                        get_token(T.Whitespace, ' '),
                                        get_token(T.Keyword, 'END'),
                                    ]),
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
                        ]),
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

    def test_012_non_reserved_keywords(self):
        # NAME is a non-reserved keyword
        p = PostgresParser()
        sql_text = '''
            SELECT name, elevation
            FROM ONLY cities;
        '''
        exp_stmt = [
            PostgresSqlStatement(ttype=ST.Select, token_list=[
                TokenGroup(ttype=ST.SelectClause, token_list=[
                    get_token(T.Keyword, 'SELECT'),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.Identifier, token_list=[
                        get_token(T.Name, 'name'),
                    ]),
                    get_token(T.Punctuation, ','),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.Identifier, token_list=[
                        get_token(T.Name, 'elevation'),
                    ]),
                ]),

                get_token(T.Whitespace, ' '),

                TokenGroup(ttype=ST.FromClause, token_list=[
                    get_token(T.Keyword, 'FROM'),
                    get_token(T.Whitespace, ' '),
                    get_token(T.Keyword, 'ONLY'),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.Identifier, token_list=[
                        get_token(T.Name, 'cities'),
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

    def test_013_with_non_recursive(self):
        p = PostgresParser()
        sql_text = '''
            WITH regional_sales AS (
                SELECT region, SUM(amount) AS total_sales
                FROM orders
                GROUP BY region
            ), top_regions AS (
                SELECT region
                FROM regional_sales
                WHERE total_sales > (SELECT SUM(total_sales)/10 FROM regional_sales)
            )
            SELECT region,
                product,
                SUM(quantity) AS product_units,
                SUM(amount) AS product_sales
            FROM orders
            WHERE region IN (SELECT region FROM top_regions)
            GROUP BY region, product;
        '''
        exp_stmt = [
            PostgresSqlStatement(ttype=ST.Select, token_list=[
                TokenGroup(ttype=PT.WithClause, token_list=[
                    get_token(T.Keyword, 'WITH'),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=PT.WithIdentifier, token_list=[
                        get_token(PT.WithQueryAliasName, 'regional_sales'),
                        get_token(T.Whitespace, ' '),
                        get_token(T.Keyword, 'AS'),
                        get_token(T.Whitespace, ' '),
                        TokenGroup(ttype=ST.SubQuery, token_list=[
                            get_token(T.Punctuation, '('),
                            get_token(T.Whitespace, ' '),
                            TokenGroup(ttype=ST.SelectClause, token_list=[
                                get_token(T.Keyword, 'SELECT'),
                                get_token(T.Whitespace, ' '),
                                TokenGroup(ttype=ST.Identifier, token_list=[
                                    get_token(T.Name, 'region'),
                                ]),
                                get_token(T.Punctuation, ','),
                                get_token(T.Whitespace, ' '),
                                TokenGroup(ttype=ST.Function, token_list=[
                                    get_token(T.Name, 'SUM'),
                                    TokenGroup(ttype=ST.ArgumentList, token_list=[
                                        get_token(T.Punctuation, '('),
                                        TokenGroup(ttype=ST.Identifier, token_list=[
                                            get_token(T.Name, 'amount'),
                                        ]),
                                        get_token(T.Punctuation, ')')
                                    ]),
                                    get_token(T.Whitespace, ' '),
                                    get_token(T.Keyword, 'AS'),
                                    get_token(T.Whitespace, ' '),
                                    get_token(ST.AliasName, 'total_sales'),
                                ]),
                            ]),
                            get_token(T.Whitespace, ' '),
                            TokenGroup(ttype=ST.FromClause, token_list=[
                                get_token(T.Keyword, 'FROM'),
                                get_token(T.Whitespace, ' '),
                                TokenGroup(ttype=ST.Identifier, token_list=[
                                    get_token(T.Name, 'orders'),
                                ]),
                            ]),
                            get_token(T.Whitespace, ' '),
                            TokenGroup(ttype=ST.GroupByClause, token_list=[
                                get_token(T.Keyword, 'GROUP'),
                                get_token(T.Whitespace, ' '),
                                get_token(T.Keyword, 'BY'),
                                get_token(T.Whitespace, ' '),
                                TokenGroup(ttype=ST.Identifier, token_list=[
                                    get_token(T.Name, 'region'),
                                ]),
                            ]),
                            get_token(T.Whitespace, ' '),
                            get_token(T.Punctuation, ')'),
                        ]),
                    ]),
                    get_token(T.Punctuation, ','),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=PT.WithIdentifier, token_list=[
                        get_token(PT.WithQueryAliasName, 'top_regions'),
                        get_token(T.Whitespace, ' '),
                        get_token(T.Keyword, 'AS'),
                        get_token(T.Whitespace, ' '),
                        TokenGroup(ttype=ST.SubQuery, token_list=[
                            get_token(T.Punctuation, '('),
                            get_token(T.Whitespace, ' '),
                            TokenGroup(ttype=ST.SelectClause, token_list=[
                                get_token(T.Keyword, 'SELECT'),
                                get_token(T.Whitespace, ' '),
                                TokenGroup(ttype=ST.Identifier, token_list=[
                                    get_token(T.Name, 'region'),
                                ]),
                            ]),
                            get_token(T.Whitespace, ' '),
                            TokenGroup(ttype=ST.FromClause, token_list=[
                                get_token(T.Keyword, 'FROM'),
                                get_token(T.Whitespace, ' '),
                                TokenGroup(ttype=ST.Identifier, token_list=[
                                    get_token(T.Name, 'regional_sales'),
                                ]),
                            ]),
                            get_token(T.Whitespace, ' '),
                            TokenGroup(ttype=ST.WhereClause, token_list=[
                                get_token(T.Keyword, 'WHERE'),
                                get_token(T.Whitespace, ' '),
                                TokenGroup(ttype=ST.Comparison, token_list=[
                                    TokenGroup(ttype=ST.Identifier, token_list=[
                                        get_token(T.Name, 'total_sales'),
                                    ]),
                                    get_token(T.Whitespace, ' '),
                                    get_token(ST.ComparisonOperator, '>'),
                                    get_token(T.Whitespace, ' '),
                                    TokenGroup(ttype=ST.SubQuery, token_list=[
                                        get_token(T.Punctuation, '('),
                                        TokenGroup(ttype=ST.SelectClause, token_list=[
                                            get_token(T.Keyword, 'SELECT'),
                                            get_token(T.Whitespace, ' '),
                                            TokenGroup(ttype=ST.ComputedIdentifier, token_list=[
                                                TokenGroup(ttype=ST.Function, token_list=[
                                                    get_token(T.Name, 'SUM'),
                                                    TokenGroup(ttype=ST.ArgumentList, token_list=[
                                                        get_token(
                                                            T.Punctuation, '('),
                                                        TokenGroup(ttype=ST.Identifier, token_list=[
                                                            get_token(
                                                                T.Name, 'total_sales'),
                                                        ]),
                                                        get_token(
                                                            T.Punctuation, ')')
                                                    ]),
                                                ]),
                                                get_token(T.Operator, '/'),
                                                get_token(
                                                    T.Number.Integer, '10'),
                                            ]),
                                        ]),
                                        get_token(T.Whitespace, ' '),
                                        TokenGroup(ttype=ST.FromClause, token_list=[
                                            get_token(T.Keyword, 'FROM'),
                                            get_token(T.Whitespace, ' '),
                                            TokenGroup(ttype=ST.Identifier, token_list=[
                                                get_token(
                                                    T.Name, 'regional_sales'),
                                            ]),
                                        ]),
                                        get_token(T.Punctuation, ')'),
                                    ]),
                                ]),
                            ]),
                            get_token(T.Whitespace, ' '),
                            get_token(T.Punctuation, ')'),
                        ]),
                    ]),
                ]),

                get_token(T.Whitespace, ' '),

                TokenGroup(ttype=ST.SelectClause, token_list=[
                    get_token(T.Keyword, 'SELECT'),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.Identifier, token_list=[
                        get_token(T.Name, 'region'),
                    ]),
                    get_token(T.Punctuation, ','),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.Identifier, token_list=[
                        get_token(T.Name, 'product'),
                    ]),
                    get_token(T.Punctuation, ','),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.Function, token_list=[
                        get_token(T.Name, 'SUM'),
                        TokenGroup(ttype=ST.ArgumentList, token_list=[
                            get_token(T.Punctuation, '('),
                            TokenGroup(ttype=ST.Identifier, token_list=[
                                get_token(T.Name, 'quantity'),
                            ]),
                            get_token(T.Punctuation, ')')
                        ]),
                        get_token(T.Whitespace, ' '),
                        get_token(T.Keyword, 'AS'),
                        get_token(T.Whitespace, ' '),
                        get_token(ST.AliasName, 'product_units'),
                    ]),
                    get_token(T.Punctuation, ','),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.Function, token_list=[
                        get_token(T.Name, 'SUM'),
                        TokenGroup(ttype=ST.ArgumentList, token_list=[
                            get_token(T.Punctuation, '('),
                            TokenGroup(ttype=ST.Identifier, token_list=[
                                get_token(T.Name, 'amount'),
                            ]),
                            get_token(T.Punctuation, ')')
                        ]),
                        get_token(T.Whitespace, ' '),
                        get_token(T.Keyword, 'AS'),
                        get_token(T.Whitespace, ' '),
                        get_token(ST.AliasName, 'product_sales'),
                    ]),
                ]),

                get_token(T.Whitespace, ' '),

                TokenGroup(ttype=ST.FromClause, token_list=[
                    get_token(T.Keyword, 'FROM'),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.Identifier, token_list=[
                        get_token(T.Name, 'orders'),
                    ]),
                ]),

                get_token(T.Whitespace, ' '),

                TokenGroup(ttype=ST.WhereClause, token_list=[
                    get_token(T.Keyword, 'WHERE'),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.In, token_list=[
                        TokenGroup(ttype=ST.Identifier, token_list=[
                            get_token(T.Name, 'region'),
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
                                    get_token(T.Name, 'region'),
                                ]),
                            ]),
                            get_token(T.Whitespace, ' '),
                            TokenGroup(ttype=ST.FromClause, token_list=[
                                get_token(T.Keyword, 'FROM'),
                                get_token(T.Whitespace, ' '),
                                TokenGroup(ttype=ST.Identifier, token_list=[
                                    get_token(T.Name, 'top_regions'),
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
                        get_token(T.Name, 'region'),
                    ]),
                    get_token(T.Punctuation, ','),
                    get_token(T.Whitespace, ' '),
                    TokenGroup(ttype=ST.Identifier, token_list=[
                        get_token(T.Name, 'product'),
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
