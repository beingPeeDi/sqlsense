''' Extends the Statement class used for Postgres SQL parsing.
    Parts of the code are similar to / copied from sqlparse: https://github.com/andialbrecht/sqlparse
'''

from pygments import token as T

import sqlsense.postgres.postgres_tokens as PT
import sqlsense.tokens as ST
from sqlsense.sql import SqlStatement, Token


class PostgresSqlStatement(SqlStatement):
    ''' SQL Statement class
    '''

    def __init__(self, token_list=None, ttype=None, default_catalog=None, default_schema=None):
        super().__init__(token_list=token_list, ttype=ttype)
        self._default_catalog = default_catalog
        self._default_schema = default_schema
        self._datasets = None
        self._datafields = None

    @property
    def default_catalog(self):
        return self._default_catalog

    @property
    def default_schema(self):
        return self._default_schema

    def get_identifiers(self):
        return super().get_identifiers(tokengroup_set={PT.WithIdentifier, })

    def datasets_involved(self):
        """ Returns a list of datasets involved in the Postgres 
        SQL Statement.
        Dataset information is generated from the parsed token list
        when the function is called for the first time and stored.
        On subsequent calls, the stored information is returned.

        Returns:
            [List] -- List of Datasets involved in the Postgres
            SQL Statement.
            {type, dataset, schema, catalog, alias, rr_ind, defined_at}
        """
        if self._datasets is None:
            # Datasets info needs to be generated.
            self._datasets = []
            for token in self.get_identifiers():
                if token.parent.ttype in (ST.FromClause, PT.WithClause):
                    _dataset = {
                        'type': 'NotKnown',
                        'dataset': '',
                        'schema': self._default_schema,
                        'catalog': self._default_catalog,
                        'alias': None,
                        'rw_ind': 'r',
                        'defined_at': token,
                    }
                    if token.ttype == ST.SubQuery:
                        _dataset['type'] = 'Sub Query'
                        subquery_ind = True
                        for subquery_token in token.token_list:
                            if subquery_token.ttype == ST.AliasName:
                                _dataset['alias'] = subquery_token.value()
                                subquery_ind = False
                            elif subquery_token.match_type_value(Token(T.Keyword, 'AS')):
                                subquery_ind = False
                            if subquery_ind:
                                _dataset['dataset'] = _dataset['dataset'] + \
                                    subquery_token.value(True)
                    elif token.ttype == PT.WithIdentifier:
                        _dataset['type'] = 'With Query'
                        for subtoken in token.token_list:
                            if subtoken.ttype == PT.WithQueryAliasName:
                                _dataset['alias'] = subtoken.value()
                            elif subtoken.ttype == PT.WithQueryAliasIdentifier:
                                for subsubtoken in subtoken.token_list:
                                    if subsubtoken.ttype == PT.WithQueryAliasName:
                                        _dataset['alias'] = subtoken.value()
                            elif subtoken.ttype == ST.SubQuery:
                                _dataset['dataset'] = subtoken.value()
                    else:
                        _dataset['type'] = 'Dataset'
                        qualifier = []
                        for sub_token in token.token_list:
                            if sub_token.ttype == T.Name:
                                _dataset['dataset'] = sub_token.value()
                            elif sub_token.ttype == ST.AliasName:
                                _dataset['alias'] = sub_token.value()
                            elif sub_token.ttype == ST.QualifierName:
                                qualifier.append(sub_token.value())
                        if len(qualifier) >= 1:
                            _dataset['schema'] = qualifier[-1]
                        if len(qualifier) == 2:
                            _dataset['catalog'] = qualifier[-2]
                    self._datasets.append(_dataset)
        return self._datasets

    def datafields_involved(self):
        """ Returns a list of datafields involved in the Postgres 
        SQL Statement.
        Datafield information is generated from the parsed token list
        when the function is called for the first time and stored.
        On subsequent calls, the stored information is returned.

        Returns:
            [List] -- List of Datafields involved in the Postgres
            SQL Statement.
            {type, datafield, dataset, schema, catalog, dataset_alias, datafield_alias, rr_ind, defined_at}
        """
        if self._datafields is None:
            # Datafields info needs to be generated.
            self.datasets_involved()
            self._datafields = []
            for token in self.get_identifiers():
                if token.parent.ttype not in (ST.FromClause, ):
                    _datafield = {
                        'type': 'NotKnown',
                        'datafield': '',
                        'datafield_alias': None,
                        'dataset': None,
                        'schema': None,
                        'catalog': None,
                        'dataset_type': None,
                        'dataset_alias': None,
                        'rw_ind': 'r',
                        'defined_at': token,
                    }
                    if token.ttype == ST.Identifier:
                        _datafield['type'] = 'Datafield'
                        for sub_token in token.token_list:
                            if sub_token.ttype in (T.Name, ST.AllColumnsIdentifier):
                                _datafield['datafield'] = sub_token.value()
                            elif sub_token.ttype == ST.AliasName:
                                _datafield['datafield_alias'] = sub_token.value()
                            elif sub_token.ttype == ST.QualifierName:
                                _datafield['dataset_alias'] = sub_token.value()
                        # Get Dataset info
                        if _datafield['dataset_alias']:
                            dataset_alias_found = False
                            for dset in self._datasets:
                                # Using Alias
                                if _datafield['dataset_alias'] == dset['alias']:
                                    _datafield['dataset'] = dset['dataset']
                                    _datafield['dataset_type'] = dset['type']
                                    _datafield['schema'] = dset['schema']
                                    _datafield['catalog'] = dset['catalog']
                                    dataset_alias_found = True
                                    break
                            if not dataset_alias_found:
                                for dset in self._datasets:
                                    # Using Dataset Name
                                    if _datafield['dataset_alias'] == dset['dataset']:
                                        _datafield['dataset'] = dset['dataset']
                                        _datafield['dataset_type'] = dset['type']
                                        _datafield['schema'] = dset['schema']
                                        _datafield['catalog'] = dset['catalog']
                                        break
                    elif token.ttype in (ST.ComputedIdentifier, ST.SelectConstantIdentifier, ST.Function):
                        _datafield['type'] = 'Computed Field' if token.ttype == ST.ComputedIdentifier else (
                            'Function Field' if token.ttype == ST.Function else 'Constant Field')
                        not_an_alias_ind = True
                        for sub_token in token.token_list:
                            if sub_token.ttype == ST.AliasName:
                                _datafield['datafield_alias'] = sub_token.value()
                                not_an_alias_ind = False
                            elif sub_token.match_type_value(Token(T.Keyword, 'AS')):
                                not_an_alias_ind = False
                            if not_an_alias_ind:
                                _datafield['datafield'] = _datafield['datafield'] + \
                                    sub_token.value(True)
                    else:
                        # No need to process
                        continue
                    self._datafields.append(_datafield)
        return self._datafields
