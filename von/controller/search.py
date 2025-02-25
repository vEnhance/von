import logging

from .. import model, view

parser = view.Parser(
    prog="search", description="Searches for problems by tags or text."
)
parser.add_argument(
    "s_terms", nargs="*", metavar="term", help="Terms you want to search for."
)
parser.add_argument(
    "-t",
    "--tag",
    nargs="+",
    metavar="tag",
    dest="s_tags",
    default=[],
    help="Tags you want to search for.",
)
parser.add_argument(
    "-k",
    "--source",
    nargs="+",
    metavar="source",
    dest="s_sources",
    default=[],
    help="Sources you want to search for.",
)
parser.add_argument(
    "-w",
    "--authors",
    nargs="+",
    metavar="authors",
    dest="s_authors",
    default=[],
    help="Authors you want to search for.",
)
parser.add_argument(
    "-r",
    "--refine",
    action="store_true",
    help="Prune through the Cache rather than the whole database.",
)
parser.add_argument(
    "-a",
    "--alphabetical",
    action="store_true",
    help="Sort the results alphabetically, not by sort tag.",
)
parser.add_argument(
    "-e", "--everything", action="store_true", help="Allow searching everything."
)
otis_group = parser.add_mutually_exclusive_group()
otis_group.add_argument(
    "-n", "--notused", action="store_true", help="Problem not used in OTIS"
)
otis_group.add_argument(
    "-o", "--occupied", action="store_true", help="Problem used in OTIS"
)
url_group = parser.add_mutually_exclusive_group()
url_group.add_argument(
    "-l", "--linked", action="store_true", help="Problem has a URL provided"
)
url_group.add_argument(
    "-u", "--unlinked", action="store_true", help="Problem has no URL provided"
)


def main(self: object, argv: list[str]):
    opts = parser.process(argv)

    query_is_empty = (
        len(opts.s_terms + opts.s_tags + opts.s_sources + opts.s_authors) == 0
    )

    if opts.everything is False and query_is_empty is True:
        logging.warning(
            "Must supply at least one search keyword or pass --everything option."
        )
        return
    if opts.everything is True and query_is_empty is False:
        logging.warning("Passing --everything with parameters makes no sense.")
        return

    if opts.notused is True:
        in_otis = False
    elif opts.occupied is True:
        in_otis = True
    else:
        in_otis = None

    if opts.unlinked is True:
        has_url = False
    elif opts.linked is True:
        has_url = True
    else:
        has_url = None

    search_path = model.getcwd()
    if search_path != "":
        logging.info(
            "Search restricted to "
            + view.APPLY_COLOR("BOLD_GREEN", view.formatPath(search_path))
        )
    result = model.runSearch(
        terms=opts.s_terms,
        tags=opts.s_tags,
        sources=opts.s_sources,
        authors=opts.s_authors,
        refine=opts.refine,
        path=search_path,
        alph_sort=opts.alphabetical,
        in_otis=in_otis,
        has_url=has_url,
    )

    for entry in result:
        view.printEntry(entry)
    if len(result) == 0:
        logging.warning("No matches found.")
