import unittest

from common.syntax.syntax import MermaidSyntaxImpl


class TestMermaidSyntaxImpl(unittest.TestCase):
	def setUp(self):
		self.syntax = MermaidSyntaxImpl("")

	def test_start(self):
		self.syntax.start()
		self.assertEqual(
			"""```mermaid
flowchart TD
""",
			self.syntax.syntax,
		)

	def test_add(self):
		self.syntax.start()

		self.syntax.add("cikini", "gondangdia")
		self.assertEqual(
			"""```mermaid
flowchart TD
  cikini --> gondangdia
""",
			self.syntax.syntax,
		)

	def test_finish(self):
		self.syntax.start()
		self.syntax.add("cikini", "gondangdia")

		self.syntax.finish()
		self.assertEqual(
			"""```mermaid
flowchart TD
  cikini --> gondangdia
```
""",
			self.syntax.syntax,
		)
