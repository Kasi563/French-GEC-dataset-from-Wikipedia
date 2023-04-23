"""
French Wikipedia markup cleaning tool inspired by daemon's pywikipclean (https://github.com/daemon/pywikiclean).
Two functions are provided:
    - A pre cleaner function for pre cleaning: pre_cleaner
    - And a post cleaning function for post cleaning: post_cleaner
"""

from difflib import context_diff
import html
import re
import clean_templates as ct

# Regex patterns
FOOTER_PATT = "(==\\s*Voir aussi\\s*==.*|==\\s*Notes et références\\s*==.*|==\\s*Further " + \
    "reading\\s*==.*|==\\s*Liens externes\\s*==.*|==\\s*Articles connexes" + \
    "\\s*==.*|==\\s*Lien externe\\s*==.*|==\\s*Données statistiques\\s*==.*|==\\s*Statistiques\\s*==.*)"
CATEGORY_LINKS = re.compile("\\[\\[Category:([^\\]]+)\\]\\]")
HEADINGS = re.compile("=+\\s?(.*?)=+")
HTML_COMMENT_EMPHASIS = re.compile("((<|&lt;|&#60;)!--.*?--(>|&gt;|&#62;)|('''|''))", re.DOTALL)
HTML_TAGS = re.compile("<[^>]+>")
INDENTATION = re.compile("[\\n\\r]:\\s*")
INTER_WIKI_LINKS = re.compile("\\[\\[[a-z\\-]+:[^|\\]]+\\]\\]")
IPA = re.compile("( (\\(|\\[)\\{\\{IPA[^\\}]+\\}\\}(\\)|\\])| \\{\\{IPA[^\\}]+\\}\\})")
LINKS1 = re.compile("\\[\\[[^\\]]+\\|([^\\]]+)\\]\\]")
LINKS2 = re.compile("(\\[\\[|\\]\\])")
MATH_GALLERY_NO_TOC = re.compile("(__NOTOC__|&lt;gallery&gt;.*?&lt;/gallery&gt;|&lt;math&gt;.*?&lt;/math&gt;)")
MULTIPLE_NEWLINES = re.compile("[\\n\\r][\\n\\r]+")
REFS = re.compile("(&lt;br */&gt;|&lt;ref[^/]+/&gt;|&lt;ref.*?&lt;/ref&gt;)", re.DOTALL);
UNIT_CONVERSION1 = re.compile("\\{\\{convert\\|(\\d+)\\|([^|]+)\\}\\}")
UNIT_CONVERSION2 = re.compile("\\{\\{convert\\|(\\d+)\\|([^|]+)\\|[^}]+\\}\\}")
MULT_NL_PATT = re.compile("[\\n\\r][\\n\\r]+")
REF_PATT = re.compile("<ref.*?>.+?<\/ref>")

# other patterns
P2 = re.compile(r"<ref>(?=[A-Z])")



# Check title
special_title_prefix = ["Média", "Spécial", "Discussion", "Utilisateur", "Discussion utilisateur", "Wikipédia", "Discussion Wikipédia", "Fichier", "Discussion fichier", "MediaWiki", "Discussion MediaWiki", "Modèle", "Discussion modèle", "Aide", "Discussion aide", "Catégorie", "Discussion catégorie", "Portail", "Discussion Portail", "Projet", "Discussion Projet", "Référence", "Discussion Référence", "TimedText", "TimedText talk", "Module", "Discussion module", "Gadget", "Discussion gadget", "Définition de gadget", "Discussion définition de gadget", "Sujet"]

def pre_cleaner(content: str):
    """
    Pre-cleans the given text: removes headings and sections:
        Voir aussi; Notes et références; Liens externes; Articles connexes; Lien externe; Données statistiques; Statistiques
    Removes <refs> tags
    Cleans or removes templates.
    Args: 
        content: corpus of text
    """
    content = re.sub(FOOTER_PATT, "", content)
    content = re.sub(HEADINGS, "", content)
    content = remove_image_captions(content)
    content = remove_table(content)
    content = re.sub(REF_PATT, "", content)
    content = ct.remove_templates(ct.remove_templates(content))
    content = remove_double_bracket(content)
    return content


def remove_image_captions(s):
    return _remove_image_caption(_remove_image_caption(s, "[[File:"), "[[Image:")


def _remove_image_caption(s, label):
    DEFAULT = 0
    STATE_1CLOSE_BRACE = 1
    STATE_1OPEN_BRACE = 2

    i = s.find(label)
    while i != -1:
        state = DEFAULT
        level = 1
        cur = i + len(label)
        while cur < len(s):
            if state == STATE_1OPEN_BRACE and s[cur] == "[":
                level += 1
                state = DEFAULT
            if state == STATE_1OPEN_BRACE:
                state = DEFAULT
            if s[cur] == "[":
                state = STATE_1OPEN_BRACE
            if state == STATE_1CLOSE_BRACE and s[cur] == "]":
                level -= 1
                if level == 0:
                    break
                state = DEFAULT
            else:
                if state == STATE_1CLOSE_BRACE:
                    state = DEFAULT
                if s[cur] == "]":
                    state = STATE_1CLOSE_BRACE
            cur += 1
        if (cur == len(s)):
            return s[:i]
        s = f"{s[:i]}{s[cur + 1:]}"
        i = s.find(label, i)
    return s 


def remove_double_bracket(s):
    DEFAULT = 0
    STATE_1CLOSE_BRACE = 1
    STATE_1OPEN_BRACE = 2

    i = s.find("{{")
    while i != -1:
        state = DEFAULT
        level = 1
        cur = i + 2
        while cur < len(s):
            if state == STATE_1OPEN_BRACE and s[cur] == "{":
                level += 1
                state = DEFAULT
            if state == STATE_1OPEN_BRACE:
                state = DEFAULT
            if s[cur] == "{":
                state = STATE_1OPEN_BRACE
            if state == STATE_1CLOSE_BRACE and s[cur] == "}":
                level -= 1
                if level == 0:
                    break
                state = DEFAULT
            else:
                if state == STATE_1CLOSE_BRACE:
                    state = DEFAULT
                if s[cur] == "}":
                    state = STATE_1CLOSE_BRACE
            cur += 1
        if (cur == len(s)):
            return s[:i]
        s = f"{s[:i]}{s[cur + 1:]}"
        i = s.find("{{", i + 1)
    return s


def remove_table(s):
    DEFAULT = 0
    STATE_PIPE = 1
    STATE_1OPEN_BRACE = 2

    i = s.find("{|")
    while i != -1:
        state = DEFAULT
        level = 1
        cur = i + 2
        while cur < len(s):
            if state == STATE_1OPEN_BRACE and s[cur] == "|":
                level += 1
                state = DEFAULT
            if state == STATE_1OPEN_BRACE:
                state = DEFAULT
            if s[cur] == "{":
                state = STATE_1OPEN_BRACE
            if state == STATE_PIPE and s[cur] == "}":
                level -= 1
                if level == 0:
                    break
                state = DEFAULT
            else:
                if state == STATE_PIPE:
                    state = DEFAULT
                if s[cur] == "|":
                    state = STATE_PIPE
            cur += 1
        if (cur == len(s)):
            return s[:i]
        s = f"{s[:i]}{s[cur + 1:]}"
        i = s.find("{|", i)
    return s


def post_cleaner(content: str):
    """
    Cleans wikimarkup text completely.
    Args:
        content: string of wikimarkup text
    """
    content = re.sub(REFS, "", content)
    content = re.sub(INTER_WIKI_LINKS, " ", content)
    content = re.sub(IPA, "", content)
    content = re.sub(UNIT_CONVERSION1, r"\1 \2", content)
    content = re.sub(UNIT_CONVERSION2, r"\1 \2", content)
    content = re.sub(HTML_COMMENT_EMPHASIS, "", content)
    content = re.sub(CATEGORY_LINKS, "", content)
    content = re.sub(LINKS1, r"\1", content)
    content = re.sub(LINKS2, "", content)
    content = re.sub(MATH_GALLERY_NO_TOC, "", content)
    content = re.sub(INDENTATION, "\n", content)
    content = html.unescape(html.unescape(content))
    content = re.sub(HTML_TAGS, "", content)

    return re.sub(MULT_NL_PATT, "\n\n", content).strip()


def filter_direct_matches(text1: list, text2: list):
    """
    Takes lists of string and returns only the strings that doesn't completely match.
    Args: 
        text1: a list of strings
        text2: a list of strings
    """
    rwm1 = []
    rwm2 = []
    text1 = [i + "\n" for i in text1 if not i[-2:-1] == "\n" or not i == "\n\n"]
    text2 = [i + "\n" for i in text2 if not i[-2:-1] == "\n" or not i == "\n\n"]
    count = 0
    switch = False
    for sentence in context_diff(text1, text2):
        count += 1
        if count > 4:
            first_char = sentence[0]
            if sentence[:3] == "---":
                switch = True
            if first_char == "!" or first_char == "+":
                if switch:
                    rwm2.append(sentence)
                else:
                    rwm1.append(sentence)
    return rwm1, rwm2



SENT_PATT2 = re.compile(r"[A-Z*ÀÂÆÇÉÈÊËÎÏÔŒÙÛÜŸ].+?[.!?]{1,3}(?=\s|$)")
def split_text(corpus: str) -> list[str]:
    """
    Splits a corpus of text into sentences.
    Args:
        - corpus: A string.
    """
    try:
        result = re.findall(SENT_PATT2, corpus)
    except TypeError:
        return []
    return result


# def split_text_regex(corpus):
#     result = []
#     try:
#         for sentence in re.split(SENT_PATT2, corpus):
#             result.append(sentence)
#     except TypeError:
#         print(corpus)
#         return []
#     return result


def check_title(title: str):
    """
    Checks it the title of the page is not a title that is undesirable like for example a discussion page.
    If title is 'undesirable', returns True. Otherwise returns False.
    Arg:
        - title: string, title of the wikipedia page.
    """
    for s in special_title_prefix:
        if s + ":" in title:
            return True
    return False
