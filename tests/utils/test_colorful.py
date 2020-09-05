import pytest
from colorama import Fore as F, Style
from langumo.utils import colorful

R = Style.RESET_ALL


def test_colorful_rendering():
    assert colorful.render('hello world') == f'hello world{R}'

    assert (colorful.render('hello <k>world!</k>')
            == f'hello {R}{F.BLACK}world!{R}{R}')
    assert (colorful.render('<r>hello</r> world!')
            == f'{R}{F.RED}hello{R} world!{R}')

    assert (colorful.render('<g>hello</g> <y>world!</y>')
            == f'{R}{F.GREEN}hello{R} {R}{F.YELLOW}world!{R}{R}')
    assert (colorful.render('<b>hello</b> <m>world!</m>')
            == f'{R}{F.BLUE}hello{R} {R}{F.MAGENTA}world!{R}{R}')

    assert (colorful.render('<c></c>hello<w> </w>world!')
            == f'{R}{F.CYAN}{R}hello{R}{F.WHITE} {R}world!{R}')


def test_rendering_wrong_colors():
    with pytest.raises(ValueError):
        colorful.render('<a>this is a text with wrong color.</a>')
