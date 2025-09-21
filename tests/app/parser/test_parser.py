import unittest

from sqlglot import exp, parse_one

import common.errors.errors as commonerr
from app.parser.parser import ParserImpl
from common.syntax.syntax import MermaidSyntaxImpl


class TestParserImpl(unittest.TestCase):
	def test_get_root(self) -> None:
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
				"caseName": "get structure successfully",
				"query": "select * from datamart.events.daily",
				"expectedStructure": """```mermaid
flowchart TD
  datamart.events.daily --> final_select
```
""",
				"expectedErr": None,
			},
		]

		for c in cases:
			with self.subTest(c["caseName"]):
				mermaid_syntax = MermaidSyntaxImpl("")
				parser = ParserImpl(c["query"], mermaid_syntax)

				if c["expectedErr"] is None:
					structure = parser.get_root()
					self.assertEqual(structure, c["expectedStructure"])
				else:
					with self.assertRaises(c["expectedErr"]):
						parser.get_root()

	def test_handle_structure(self) -> None:
		cases = [
			{
				"caseName": "select from CTE",
				"query": """
with q as (
	select * from datamart.events.daily
)

select * from q
""",
				"expectedStructure": """```mermaid
flowchart TD
  datamart.events.daily --> q
  q --> final_select
```
""",
			},
			{
				"caseName": "select from nested CTE",
				"query": """
with q as (
	with qq as (
		select * from datamart.events.daily
	)

	select * from qq
)

select * from q
""",
				"expectedStructure": """```mermaid
flowchart TD
  datamart.events.daily --> qq
  qq --> q
  q --> final_select
```
""",
			},
			{
				"caseName": "select from nested subquery",
				"query": """
select * from (
	select * from (
		select * from datamart.events.daily
	)
)
""",
				"expectedStructure": """```mermaid
flowchart TD
  datamart.events.daily --> final_select
```
""",
			},
			{
				"caseName": "select from nested subquery with alias",
				"query": """
select * from (
	select * from (
		select * from datamart.events.daily
	) d
)
""",
				"expectedStructure": """```mermaid
flowchart TD
  d --> final_select
  datamart.events.daily --> d
```
""",
			},
			{
				"caseName": "select from CTE containing subquery",
				"query": """
with q as (
	select * from (
		select * from datamart.events.daily
	)
)

select * from q
""",
				"expectedStructure": """```mermaid
flowchart TD
  datamart.events.daily --> q
  q --> final_select
```
""",
			},
			{
				"caseName": "select from CTE containing subquery with alias",
				"query": """
with q as (
	select * from (
		select * from datamart.events.daily
	) d
)

select * from q
""",
				"expectedStructure": """```mermaid
flowchart TD
  d --> q
  datamart.events.daily --> d
  q --> final_select
```
""",
			},
			{
				"caseName": "select from subquery, with alias, containing CTE",
				"query": """
select * from (
    with q as (
        select * from datamart.events.daily
    )

    select * from q
) d
""",
				"expectedStructure": """```mermaid
flowchart TD
  d --> final_select
  datamart.events.daily --> q
  q --> d
```
""",
			},
		]

		for c in cases:
			with self.subTest(c["caseName"]):
				mermaid_syntax = MermaidSyntaxImpl("")
				parser = ParserImpl(c["query"], mermaid_syntax)

				root = parse_one(c["query"], dialect="bigquery").find(exp.Select)
				mermaid_syntax.start()
				parser.handle_structure(root)
				mermaid_syntax.finish()

				structure = mermaid_syntax.syntax
				self.assertEqual(structure, c["expectedStructure"])

	def test_walk_source(self) -> None:
		cases = [
			{
				"caseName": "select from table",
				"query": "select * from datamart.events.daily",
				"expectedStructure": """```mermaid
flowchart TD
  datamart.events.daily --> final_select
```
""",
			},
			{
				"caseName": "select from table with alias",
				"query": "select * from datamart.events.daily d",
				"expectedStructure": """```mermaid
flowchart TD
  datamart.events.daily --> final_select
```
""",
			},
			{
				"caseName": "select from subquery",
				"query": """
select * from (
	select * from datamart.events.daily
)
""",
				"expectedStructure": """```mermaid
flowchart TD
```
""",
			},
			{
				"caseName": "select from subquery with alias",
				"query": """
select * from (
	select * from datamart.events.daily
) d
""",
				"expectedStructure": """```mermaid
flowchart TD
  d --> final_select
```
""",
			},
		]

		for c in cases:
			with self.subTest(c["caseName"]):
				mermaid_syntax = MermaidSyntaxImpl("")
				parser = ParserImpl(c["query"], mermaid_syntax)

				root = parse_one(c["query"], dialect="bigquery").find(exp.Select)
				root = root.args["from"].args["this"]
				mermaid_syntax.start()
				parser.walk_source(root)
				mermaid_syntax.finish()

				structure = mermaid_syntax.syntax
				self.assertEqual(structure, c["expectedStructure"])
