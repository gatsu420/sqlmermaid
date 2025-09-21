from sqlglot import errors as sgerr
from sqlglot import exp, parse_one

import common.errors.errors as commonerr
from common.syntax.syntax import MermaidSyntaxImpl


class ParserImpl:
	def __init__(self, query: str, mermaid_syntax: MermaidSyntaxImpl):
		self.query = query
		self.mermaid_syntax = mermaid_syntax

	def get_root(self) -> str:
		if self.query == "":
			raise commonerr.ParserErr("query is not supplied")

		try:
			tree = parse_one(self.query, dialect="bigquery").find(exp.Select)
			self.mermaid_syntax.start()
		except sgerr.ParseError as pe:
			raise commonerr.ParserErr("query is malformed") from pe
		# ParseError will only be raised if malformed syntax has at least 3 words,
		# so error need to be duplicated for shorter one
		if tree is None:
			raise commonerr.ParserErr("query is malformed")

		self.handle_structure(tree)
		self.mermaid_syntax.finish()

		return self.mermaid_syntax.syntax

	def handle_structure(self, root: exp.Expression) -> None:
		if "with" in root.args:
			for e in root.args["with"].args["expressions"]:
				self.handle_structure(e.args["this"])

		if "from" in root.args:
			source = root.args["from"].args["this"]
			self.walk_source(source)
			self.handle_structure(source.args["this"])

		if "joins" in root.args:
			for j in root.args["joins"]:
				self.walk_source(j.args["this"])
				self.handle_structure(j.args["this"])

	def walk_source(self, root: exp.Subquery | exp.Table) -> exp.Subquery | exp.Table:
		source_ggparent = root.parent.parent.parent  # pyright: ignore [reportOptionalMemberAccess]
		if source_ggparent is None:
			dest = "final_select"
			self.dest_buffer = "final_select"
		elif source_ggparent.args["alias"] is not None:
			dest = source_ggparent.args["alias"]
			self.dest_buffer = source_ggparent.args["alias"]

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
				self.dest_buffer = ""
			self.mermaid_syntax.add(source, dest)

			return root

		if root.args["alias"] is not None:
			source = root.args["alias"].sql()
			if self.dest_buffer != "":
				dest = self.dest_buffer
				self.dest_buffer = ""
			self.mermaid_syntax.add(source, dest)

		return root
