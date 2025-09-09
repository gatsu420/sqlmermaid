import unittest

import common.errors.errors as commonerr
from app.parser.parser import ParserImpl
from common.syntax.syntax import MermaidSyntaxImpl


class TestParserImpl(unittest.TestCase):
	def test_get_query_structure(self) -> None:
		cases = [
			{
				"caseName": "no query is inputted",
				"query": "",
				"expectedErr": commonerr.ParserErr,
			},
			{
				"caseName": "query has syntax error",
				"query": "asdasd",
				"expectedErr": commonerr.ParserErr,
			},
			{
				"caseName": "query has longer syntax error",
				"query": "asdasd asdasd asdasd asdasd asdasd",
				"expectedErr": commonerr.ParserErr,
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
				"expectedErr": None,
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
				"expectedErr": None,
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
				"expectedErr": None,
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
				"expectedErr": None,
			},
		]

		for c in cases:
			with self.subTest(c["caseName"]):
				mermaid_syntax = MermaidSyntaxImpl("")
				parser = ParserImpl(c["query"], mermaid_syntax)

				if not c["expectedErr"]:
					structure = parser.get_query_structure()
					self.assertEqual(c["expectedStructure"], structure)
				else:
					with self.assertRaises(c["expectedErr"]):
						parser.get_query_structure()
