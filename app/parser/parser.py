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
			for e in tree.args["with"].args["expressions"]:
				self.get_nested_cte(e)

		if "from" in tree.args:
			self.get_nested_subquery(tree.args["from"].args["this"])

		if "joins" in tree.args:
			for j in tree.args["joins"]:
				self.get_nested_subquery(j.args["this"])

		self.mermaid_syntax.finish()
		return self.mermaid_syntax.syntax

	def get_nested_cte(self, root: exp.CTE) -> exp.CTE:
		source = root.args["this"].args["from"].args["this"].sql()
		dest = root.args["alias"].sql()
		self.mermaid_syntax.add(source, dest)

		if "with" not in root.args["this"].args:
			return root

		for e in root.args["this"].args["with"].args["expressions"]:
			self.get_nested_cte(e)

		return root

	def get_nested_subquery(self, root: exp.Subquery | exp.Table) -> exp.Subquery | exp.Table:
		if root.parent.parent.parent is None:
			dest = "final_select"
			self.dest_buffer = "final_select"
		elif root.parent.parent.parent.args["alias"] is not None:
			dest = root.parent.parent.parent.args["alias"]
			self.dest_buffer = root.parent.parent.parent.args["alias"]

		if isinstance(root, exp.Table):
			if root.args["db"] is None:
				source = root.args["this"].sql()
			else:
				source = (root.args["catalog"].sql()
			  		+ "." + root.args["db"].sql()
					+ "." + root.args["this"].sql()
				)

			if self.dest_buffer != "":
				dest = self.dest_buffer

			self.mermaid_syntax.add(source, dest)
			return root

		if isinstance(root, exp.Subquery):
			if root.args["alias"] is not None:
				source = root.args["alias"].sql()

				if self.dest_buffer != "":
					dest = self.dest_buffer

				self.mermaid_syntax.add(source, dest)

			self.get_nested_subquery(root.args["this"].args["from"].args["this"])


		return root

	def get_nested_from(self, root: exp.From, symbols: dict, depth: int) -> exp.From:
		if root.parent.parent is None:
			dest = "final_select"
		else:
			if root.parent.parent.args["alias"] is not None:
				dest = root.parent.parent.args["alias"].sql()
			else:
				dest = "subquery_{}".format(depth-1)

		if isinstance(root.args["this"], exp.Table):
			if root.args["this"].args["db"] is None:
				source = root.args["this"].args["this"].sql()
			else:
				source = (root.args["this"].args["catalog"].sql()
					+ "." + root.args["this"].args["db"].sql()
					+ "." + root.args["this"].args["this"].sql()
				)
			symbols[source] = dest
			return root

		if isinstance(root.args["this"], exp.Subquery):
			if root.args["this"].args["alias"] is not None:
				source = root.args["this"].args["alias"].sql()
			else:
				source = "subquery_{}".format(depth)

			symbols[source] = dest
			self.get_nested_from(root.args["this"].args["this"].args["from"], symbols, depth+1)

		return root


	def get_named_nested_from(self, symbols: dict) -> dict:
		for k, v in symbols.items():
			if "subquery_" in k:
				if "subquery_" not in v:
					buf = v

			else:
				if "subquery_" in v:
					self.mermaid_syntax.add(k, buf)
				else:
					self.mermaid_syntax.add(k, v)
