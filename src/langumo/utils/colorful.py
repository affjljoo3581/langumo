import re
import colorama
from typing import List, Dict

# Initialize `colorama` to convert formatted texts for Windows console
# automatically.
colorama.init()

# The below regex patterns are for parsing color tags in formatted string.
_re_tag_simple = re.compile(r'<(.*?)>.*?</\1>')
_re_tag_detail = re.compile(r'<(.*?)>(.*?)</\1>')


def _parse_format_tags(fstring: str) -> List[Dict[str, str]]:
    normal = [{'text': text} for text in _re_tag_simple.split(fstring)[::2]]
    colorful = [{'color': tag.group(1), 'text': tag.group(2)}
                for tag in _re_tag_detail.finditer(fstring)]

    # Return the parsed elements with preserving their orders.
    return list(sum(zip(normal, colorful), ())) + normal[-1:]


def _encode_style_element(elem: Dict[str, str]) -> str:
    prefix = ''
    if 'color' in elem:
        if elem['color'] == 'k':
            prefix = colorama.Fore.BLACK
        elif elem['color'] == 'r':
            prefix = colorama.Fore.RED
        elif elem['color'] == 'g':
            prefix = colorama.Fore.GREEN
        elif elem['color'] == 'y':
            prefix = colorama.Fore.YELLOW
        elif elem['color'] == 'b':
            prefix = colorama.Fore.BLUE
        elif elem['color'] == 'm':
            prefix = colorama.Fore.MAGENTA
        elif elem['color'] == 'c':
            prefix = colorama.Fore.CYAN
        elif elem['color'] == 'w':
            prefix = colorama.Fore.WHITE
        else:
            raise ValueError(f'color [{elem["color"]}] is not supported.')

    return prefix + elem['text'] + colorama.Style.RESET_ALL


def render(fstring: str) -> str:
    return ''.join(_encode_style_element(elem)
                   for elem in _parse_format_tags(fstring))
