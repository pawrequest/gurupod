"""
Usage:
text =  RPostWriter.write_many() /
        RWikiWriter.write_many() /
        HtmlWriter.write_many() /
        writer_funcs.ep_markup_wiki() /
        writer_funcs.ep_markup_reddit() /
        writer_funcs.ep_markup_html()
"""

from __future__ import annotations

from .writer_oop import HtmlWriter as HtmlWriter, RPostWriter as RPostWriter, \
    RWikiWriter as RWikiWriter
