from sqlglot import errors as sgerr
from sqlglot import exp, parse_one

import common.errors.errors as commonerr
from common.syntax.syntax import MermaidSyntaxImpl


class ParserImpl:
	def __init__(self, query: str, mermaid_syntax: MermaidSyntaxImpl):
		self.query = query
		self.mermaid_syntax = mermaid_syntax

	def get_query_structure(self) -> str:
		if self.query == "":
			raise commonerr.ParserErr("query is not supplied")

		try:
			tree = parse_one(self.query, dialect="bigquery").find(exp.Select)
			self.mermaid_syntax.start()
		except sgerr.ParseError as pe:
			raise commonerr.ParserErr("query is malformed") from pe
		# ParseError will only be raised if malformed syntax has at least 3 words,
		# so error need to be duplicated for shorter one
		if not tree:
			raise commonerr.ParserErr("query is malformed")

		if "with" in tree.args:
			ctes = tree.args["with"].args["expressions"]

			for s in ctes:
				cte_name = s.args["alias"].args["this"].sql()
				cte_from = s.args["this"].args["from"].args["this"].sql()
				self.mermaid_syntax.add(cte_from, cte_name)

				if "joins" in s.args["this"].args:
					for j in s.args["this"].args["joins"]:
						cte_join = j.args["this"].args["this"].sql()
						self.mermaid_syntax.add(cte_join, cte_name)

		if "from" in tree.args:
			final_select_from = tree.args["from"].args["this"]
			self.mermaid_syntax.add(final_select_from, "final_select")

		if "joins" in tree.args:
			for j in tree.args["joins"]:
				final_select_join = j.args["this"].sql()
				self.mermaid_syntax.add(final_select_join, "final_select")

		self.mermaid_syntax.finish()
		return self.mermaid_syntax.syntax
