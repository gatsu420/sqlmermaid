class MermaidSyntaxImpl:
	def __init__(self, syntax: str):
		self.syntax = syntax

	def start(self):
		self.syntax = """```mermaid
flowchart TD
"""

	def add(self, node_from: str, node_to: str) -> None:
		self.syntax += f"  {node_from} --> {node_to}\n"

	def finish(self) -> None:
		self.syntax += "```\n"
