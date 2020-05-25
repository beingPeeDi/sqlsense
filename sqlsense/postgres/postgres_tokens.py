from pygments.token import Token

from sqlsense.tokens import Identifier, TokenGroup

LimitClause = TokenGroup.LimitClause

WithClause = TokenGroup.WithClause
WithIdentifier = TokenGroup.WithIdentifier
WithQueryAliasIdentifier = Identifier.WithQueryAliasIdentifier
WithQueryAliasName = Token.Name.WithQueryAliasName
