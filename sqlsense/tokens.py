''' Defines the Statement and TokenGroup token types.
'''
from pygments.token import Token

## Statement ###################################################################

Statement = Token.Statement

Declare = Statement.Declare
Assignment = Statement.Assignment
Control = Statement.Control
Conditional = Control.Conditional
Loop = Control.Loop

# -------------------------------------------------------------------------------
DDL = Statement.DDL  # Data Definition Language
Create = DDL.Create
CreateTable = Create.CreateTable
CreateView = Create.CreateView
CreateProcedure = Create.CreateProcedure
CreateFunction = Create.CreateFunction
Alter = DDL.Alter
Drop = DDL.Drop
Rename = DDL.Rename

# -------------------------------------------------------------------------------
DML = Statement.DML  # Data Manipulation Language
Select = DML.Select
SelectInto = DML.SelectInto
Insert = DML.Insert
InsertIntoSelect = DML.InsertIntoSelect
Update = DML.Update
Delete = DML.Delete
Truncate = DML.Truncate  # We will stick to DML because
# ........................ Truncate does not alter the table
# ........................ structure (even though you may debate its DDL)

# -------------------------------------------------------------------------------
DCL = Statement.DCL  # Data Control Language
Grant = DCL.Grant
Revoke = DCL.Revoke

# -------------------------------------------------------------------------------
TCL = Statement.TCL  # Transaction Control Language
Commit = TCL.Commit
Rollback = TCL.Rollback
Savepoint = TCL.Savepoint

# -------------------------------------------------------------------------------

## Token Group #################################################################
TokenGroup = Token.TokenGroup

SubQuery = TokenGroup.SubQuery
ComputedIdentifier = TokenGroup.ComputedIdentifier  # or Expression Identifier
Identifier = TokenGroup.Identifier
Procedure = Identifier.Procedure
Function = Identifier.Function
AllColumnsIdentifier = Identifier.AllColumnsIdentifier
SelectConstantIdentifier = Identifier.SelectConstantIdentifier

TableDef = TokenGroup.TableDef
ViewDef = TokenGroup.ViewDef
ProcedureDef = TokenGroup.ProcedureDef
FunctionDef = TokenGroup.FunctionDef
ArgumentList = TokenGroup.ArgumentList

RoundBracket = TokenGroup.RoundBracket
ConditionGroup = RoundBracket.ConditionGroup  # For Conditions within Brackets
Condition = TokenGroup.Condition
Comparison = Condition.Comparison
Between = Condition.Between
Like = Condition.Like
In = Condition.In
CollectionSet = In.CollectionSet
# Contains = Condition.Contains
Exists = Condition.Exists
Not = Condition.Not
NotBetween = Condition.NotBetween
NotLike = Condition.NotLike
NotIn = Condition.NotIn

CaseExpression = TokenGroup.CaseExpression
WhenExpression = TokenGroup.WhenExpression
ThenExpression = TokenGroup.ThenExpression
ElseExpression = TokenGroup.ElseExpression
# -------------------------------------------------------------------------------
# SELECT [ ALL | DISTINCT ] [ FIRST | TOP number-of-rows ] select-list|*
# … [ INTO { host-variable-list | variable-list | table-name } ]
# … [ FROM table-list ]
# … [ WHERE search-condition ]
# … [ GROUP BY [ expression [, …]
# … [ HAVING search-condition ]
# … [ ORDER BY { expression | integer } [ ASC | DESC ] [, …] ]

SelectClause = TokenGroup.SelectClause
SelectIntoClause = TokenGroup.SelectIntoClause
FromClause = TokenGroup.FromClause
JoinOnClause = TokenGroup.JoinOnClause
WhereClause = TokenGroup.WhereClause
GroupByClause = TokenGroup.GroupByClause
HavingClause = TokenGroup.HavingClause
OrderByClause = TokenGroup.OrderByClause

# -------------------------------------------------------------------------------
# INSERT [ INTO ] [ owner.]table-name [ ( column-name [, …] ) ]
# ... { DEFAULT VALUES | VALUES ( [ expression | DEFAULT,… ) ] }
# --- or ---
# INSERT [ INTO ] [ owner.]table-name [ ( column-name [, …] ) ]
# ... select-statement

InsertIntoClause = TokenGroup.InsertIntoClause

# -------------------------------------------------------------------------------
# DELETE [ FROM ] [ owner.]table-name
# …[ FROM table-list ]
# …[ WHERE search-condition ]

DeleteClause = TokenGroup.DeleteClause

# -------------------------------------------------------------------------------
# UPDATE table
# ... SET [column-name  = expression, …
# ... [ FROM table-expression, ]
# ... [ WHERE search-condition ]
# ... [ ORDER BY expression [ ASC | DESC ] , …]

UpdateClause = TokenGroup.UpdateClause
UpdateSetClause = TokenGroup.UpdateSetClause

# -------------------------------------------------------------------------------

CastOperator = Token.Operator.CastOperator
ComparisonOperator = Token.Operator.ComparisonOperator
LogicalOperator = Token.Operator.LogicalOperator
QualifierOperator = Token.Operator.QualifierOperator

# -------------------------------------------------------------------------------

AliasName = Token.Name.AliasName
QualifierName = Token.Name.QualifierName
