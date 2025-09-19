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

		self.handle_query(tree)

		self.mermaid_syntax.finish()
		return self.mermaid_syntax.syntax

	def handle_query(self, root: exp.Expression | None) -> None:
		if root is None:
			return

		if isinstance(root, exp.Subquery):
			self.handle_query(root.args["this"])

		if "with" in root.args:
			for e in root.args["with"].args["expressions"]:
				self.dig_cte(e)
				self.handle_query(e.args["this"])

		if "from" in root.args:
			query_source = root.args["from"].args["this"]
			self.dig_query(query_source)
			self.handle_query(query_source.args["this"])

		if "joins" in root.args:
			for j in root.args["joins"]:
				self.dig_query(j.args["this"])
				self.handle_query(j.args["this"])

	def dig_cte(self, root: exp.CTE) -> exp.CTE:
		if "with" not in root.args["this"].args:
			return root

		cte_source = root.args["this"].args["from"].args["this"]
		if not isinstance(cte_source, exp.Table):
			source = cte_source.sql()
			dest = root.args["alias"].sql()
			self.mermaid_syntax.add(source, dest)

		return root

	def dig_query(self, root: exp.Subquery | exp.Table) -> exp.Subquery | exp.Table:
		query_source_ggparent = root.parent.parent.parent
		if query_source_ggparent is None:
			dest = "final_select"
			self.dest_buffer = "final_select"
		elif query_source_ggparent.args["alias"] is not None:
			dest = query_source_ggparent.args["alias"]
			self.dest_buffer = query_source_ggparent.args["alias"]

		if isinstance(root, exp.Table):
			if root.args["db"] is None:
				source = root.args["this"].sql()
			else:
				source = (
					root.args["catalog"].sql()
					+ "."
					+ root.args["db"].sql()
					+ "."
					+ root.args["this"].sql()
				)

			if self.dest_buffer != "":
				dest = self.dest_buffer

			self.mermaid_syntax.add(source, dest)
			return root

		if root.args["alias"] is not None:
			source = root.args["alias"].sql()
			if self.dest_buffer != "":
				dest = self.dest_buffer

			self.mermaid_syntax.add(source, dest)

		return root
