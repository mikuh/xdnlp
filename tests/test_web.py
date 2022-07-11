import pytest
from xdnlp import web

def test_web_simhash():
    assert web.simhash_string("agsjfasdfad") == "[0_1_0_0_1_1_1_0_0_1_0_0_0_0_0_0_0_1_0_0_1_0_1_0_0_1_0_1_0_0_0_0_0_1_0_1_1_0_0_0_0_0_0_0_0_0_0_0_0_0_1_0_1_1_0_0_1_1_1_0_0_0_0_0]"


def test_web_html():
    assert web.html.dom_tree("<html><title>卧槽</title><div>喵喵喵</div></html>") == "3a73ef24a0b6"