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
				"caseName": "get query structure successfully",
				"query": "select * from datamart.events.source1",
				"expectedStructure": """```mermaid
flowchart TD
  datamart.events.source1 --> final_select
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
					structure = parser.get_query_structure()
					self.assertEqual(structure, c["expectedStructure"])
				else:
					with self.assertRaises(c["expectedErr"]):
						parser.get_query_structure()
