"""This script builds the github pages."""
import datetime
import io
import os
import re
import shutil
import sys
from typing import Final, Callable, List, Iterable

import markdown  # type: ignore

#: the "now" function
__DTN: Final[Callable[[], datetime.datetime]] = datetime.datetime.now


def logger(message: str) -> None:
    """
    Write a message to the log.

    :param message: the message
    """
    print(f"{__DTN()}: {message}", flush=True)


# set up the paths
source_path = os.path.abspath(sys.argv[1])
if not os.path.isdir(source_path):
    raise ValueError(f"'{source_path}' is no directory.")
dest_path = os.path.abspath(sys.argv[2])
if not os.path.isdir(dest_path):
    raise ValueError(f"'{dest_path}' is no directory.")
# set the base url
html_baseurl = "https://thomasweise.github.io/oa_data/"

logger(f"building website '{source_path}' to '{dest_path}' "
       f"for '{html_baseurl}'.")

# We want to include the contents of our GitHub README.md file.
# So first, we need to load the README.md file.
md_file = os.path.join(source_path, "README.md")
logger(f"now loading markdown sources '{md_file}'.")
md_text: str
with io.open(md_file, "rt", encoding='utf-8-sig') as reader:
    md_text = reader.read()
md_text = md_text.replace(" \n", "\n")

# Now we get a HTML fragment.
logger(f"now converting markdown sources to html.")
html_text = markdown.markdown(text=md_text.strip(),
                              output_format="html").strip()

# We want to process all links that we can find and make sure that all
# local files are copied.
regexp_link = 'href=[\'"]?([^\'" >]+)'
pattern = re.compile(regexp_link)
links: Iterable[str] = re.findall(pattern, html_text)

for link in links:
    if link.startswith("http:") or link.startswith("https:"):
        logger(f"ignoring external url '{link}'.")
        continue
    src_file = os.path.abspath(os.path.join(source_path, link))
    if os.path.isfile(src_file) and (src_file.startswith(source_path)):
        dest_file = os.path.abspath(os.path.join(dest_path, link))
        if os.path.isfile(dest_file):
            logger(f"can ignore '{src_file}' as '{dest_file}' exists.")
        else:
            logger(f"must copy '{src_file}' to '{dest_file}'.")
            dest_dir = os.path.abspath(os.path.dirname(dest_file))
            logger(f"first ensuring that '{dest_dir}' exists.")
            os.makedirs(dest_dir, exist_ok=True)
            logger(f"now copying '{src_file}' to '{dest_file}'.")
            shutil.copy(src_file, dest_file)
    else:
        logger(f"ignoring non-local file url '{link}'.")

logger("canonicalizing html.")
html_text = html_text.replace("\n", " ").replace("  ", " ") \
    .replace("  ", " ").replace("  ", " ").replace("  ", " ") \
    .replace("  ", " ").replace("  ", " ") \
    .replace("</h1> ", "</h1>").replace("</h2> ", "</h2>") \
    .replace("</h3> ", "</h3>").replace("</h4> ", "</h4>") \
    .replace("</p> ", "</p>").replace("</li> ", "</li>") \
    .replace("</ul> ", "</ul>").replace("</ol> ", "</ol>")

logger("grabbing title.")
pattern = re.compile('<h1>(.*?)</h1>')
title = re.findall(pattern, html_text)
if len(title) != 1:
    raise ValueError(
        f"There should be one title, but got '{title}' in '{html_text}'.")
logger(f"got title '{title[0]}'.")

logger("flushing the compiled README.md file.")
with io.open(os.path.join(dest_path, "index.html"), "wt",
             encoding="utf-8") as outf:
    outf.write(f"<!doctype html><html><head><title>{title[0].strip()}"
               "</title></head><body>")
    outf.write(html_text)
    outf.write("</body></html>")

logger("all done.")
