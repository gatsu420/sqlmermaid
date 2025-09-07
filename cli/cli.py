import argparse
import logging

from app.parser.parser import ParserImpl
from common.syntax.syntax import MermaidSyntaxImpl


def main():
	argparser = argparse.ArgumentParser()
	argparser.add_argument("--query", help="Query to be parsed", required=True)
	args = argparser.parse_args()

	logging.basicConfig(
		format="%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s",
		datefmt="%Y/%m/%d %H:%M:%S",
	)

	mermaid_syntax = MermaidSyntaxImpl("")
	parser = ParserImpl(args.query, mermaid_syntax)
	print(parser.get_query_structure())


if __name__ == "__main__":
	main()
