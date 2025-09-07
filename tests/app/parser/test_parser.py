import unittest

from app.parser.parser import ParserImpl
from common.syntax.syntax import MermaidSyntaxImpl


class TestParserImpl(unittest.TestCase):
	def test_get_query_structure(self) -> None:
		cases = [
			{
				"caseName": "no query is inputted",
				"query": "",
				"expectedStructure": "",
			},
			{
				"caseName": "query has syntax error",
				"query": "some nonexistent syntax",
				"expectedStructure": "",
			},
			{
				"caseName": "query doesn't have select as main statement",
				"query": "insert into source1 as select 1",
				"expectedStructure": "",
			},
			{
				"caseName": "query has CTEs with join inside them and in final select",
				"query": """
with a as (
    select * from source1
)
, b as (
    select * from source2
)
, c AS (
    select
        a.*,
    from a
    join b on
        a.id = b.id
)

select
    distinct c.*,
from c
left join qq on
    c.id = qq.id
""",
				"expectedStructure": """```mermaid
flowchart TD
  source1 --> a
  source2 --> b
  a --> c
  b --> c
  c --> final_select
  qq --> final_select
```
""",
			},
			{
				"caseName": "query has CTEs with join inside them only",
				"query": """
with a as (
    select * from source1
)
, b as (
    select * from source2
)
, c AS (
    select
        a.*,
    from a
    join b on
        a.id = b.id
)

select * from c
""",
				"expectedStructure": """```mermaid
flowchart TD
  source1 --> a
  source2 --> b
  a --> c
  b --> c
  c --> final_select
```
""",
			},
			{
				"caseName": "query doesn't have CTE but still has join",
				"query": """
select
    distinct c.*,
from c
left join qq on
    c.id = qq.id
""",
				"expectedStructure": """```mermaid
flowchart TD
  c --> final_select
  qq --> final_select
```
""",
			},
			{
				"caseName": "query doesn't have both CTE and join",
				"query": """
select
    distinct c.*,
from c
""",
				"expectedStructure": """```mermaid
flowchart TD
  c --> final_select
```
""",
			},
		]

		for c in cases:
			mermaid_syntax = MermaidSyntaxImpl("")
			parser = ParserImpl(c["query"], mermaid_syntax)
			structure = parser.get_query_structure()
			self.assertEqual(
				structure,
				c["expectedStructure"],
				'case "{}" is failed'.format(c["caseName"]),
			)
