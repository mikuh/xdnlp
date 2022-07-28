import pytest
from xdnlp import web


def test_web_simhash():
    assert web.simhash_string("agsjfasdfad") == "[0_1_0_0_1_1_1_0_0_1_0_0_0_0_0_0_0_1_0_0_1_0_1_0_0_1_0_1_0_0_0_0_0_1_0_1_1_0_0_0_0_0_0_0_0_0_0_0_0_0_1_0_1_1_0_0_1_1_1_0_0_0_0_0]"


def test_web_html():
    html = """<!DOCTYPE html>
<html>
<head> 
<meta charset="utf-8"> 
<title>喵喵喵</title> 
<script>
document.getElementById("demo").innerHTML = "Hello JavaScript!";
</script>
</head>
<body>
<a href="https://baidu.com/" target="_blank">百度一下，你就知道!</a>
<p>微信：asdaf12313</p>
<p>QQ：1345151561243</p>
<p>QQ：asdfa24213</p>18042000005
<h2>Norwegian Mountain Trip</h2>
<img border="0" src="/images/pulpit.jpg" alt="Pulpit rock" width="304" height="228">
<img src="data:image/jpg;base64,/9j/2wCEAA">
</body>
</html>"""
    assert web.html.dom_tree(html) == "3a374a73ef5edab312027e54d054d054d032ae3d3d8eb6"
    assert web.html.get_images(html) == (['/images/pulpit.jpg'], ['data:image/jpg;base64,/9j/2wCEAA'])
    assert web.html.get_images(html, "https://baidu.com") == (['https://baidu.com/images/pulpit.jpg'], ['data:image/jpg;base64,/9j/2wCEAA'])
    assert web.html.get_content(html) == "喵喵喵百度一下，你就知道!微信：asdaf12313QQ：1345151561243QQ：asdfa2421318042000005NorwegianMountainTrip"
    assert web.html.get_links(html) == ['https://baidu.com/']
    assert web.html.extract_contact(html) == {'wechat': {'asdaf12313'}, 'phone': {'18042000005'}, 'qq': {'134515156124'}}
    assert web.html.extract_contact("导师微信： chenyue8870 武汉公司背景墙logo字体设计制作.武汉百阳广告电话：13476864737QQ：641173866湖北瑞丰科技HUBEI REFAN SCIENCE&TECHNOLOGY CO.LTD") == {'wechat': {'chenyue8870'}, 'phone': {'13476864737'}, 'qq': {'641173866'}}

