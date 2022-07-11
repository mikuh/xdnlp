import re


class Html(object):

    def __init__(self):
        self.re_link = re.compile('"((http|ftp)s?://[a-zA-Z0-9_\-./]*?)"')

        self.re_title_tag = re.compile('>([^>]*?)</title>')
        self.re_title_write = re.compile('>\s*document\.title\s*=\s?([\S\s]*?);?\s*</script>')

        self.re_tag = re.compile("<(/?[a-z0-9]+?)[>\s]")

        self.tag2code = {'!--...--': '00', '!DOCTYPE': '01', 'a': '02', 'abbr': '03', 'acronym': '04', 'address': '05',
                         'applet': '06', 'area': '07', 'article': '08', 'aside': '09', 'audio': '0a', 'b': '0b',
                         'base': '0c',
                         'basefont': '0d', 'bdi': '0e', 'bdo': '0f', 'big': '10', 'blockquote': '11', 'body': '12',
                         'br': '13',
                         'button': '14', 'canvas': '15', 'caption': '16', 'center': '17', 'cite': '18', 'code': '19',
                         'col': '1a',
                         'colgroup': '1b', 'command': '1c', 'datalist': '1d', 'dd': '1e', 'del': '1f', 'details': '20',
                         'dfn': '21',
                         'dialog': '22', 'dir': '23', 'div': '24', 'dl': '25', 'dt': '26', 'em': '27', 'embed': '28',
                         'fieldset': '29', 'figcaption': '2a', 'figure': '2b', 'font': '2c', 'footer': '2d',
                         'form': '2e',
                         'frame': '2f', 'frameset': '30', 'h1': '31', 'h2': '32', 'h3': '33', 'h4': '34', 'h5': '35',
                         'h6': '36',
                         'head': '37', 'header': '38', 'hr': '39', 'html': '3a', 'i': '3b', 'iframe': '3c', 'img': '3d',
                         'input': '3e', 'ins': '3f', 'kbd': '40', 'keygen': '41', 'label': '42', 'legend': '43',
                         'li': '44',
                         'link': '45', 'main': '46', 'map': '47', 'mark': '48', 'menu': '49', 'meta': '4a',
                         'meter': '4b',
                         'nav': '4c', 'noframes': '4d', 'noscript': '4e', 'object': '4f', 'ol': '50', 'optgroup': '51',
                         'option': '52', 'output': '53', 'p': '54', 'param': '55', 'pre': '56', 'progress': '57',
                         'q': '58',
                         'rp': '59', 'rt': '5a', 'ruby': '5b', 's': '5c', 'samp': '5d', 'script': '5e', 'section': '5f',
                         'select': '60', 'small': '61', 'source': '62', 'span': '63', 'strike': '64', 'strong': '65',
                         'style': '66',
                         'sub': '67', 'summary': '68', 'sup': '69', 'table': '6a', 'tbody': '6b', 'td': '6c',
                         'textarea': '6d',
                         'tfoot': '6e', 'th': '6f', 'thead': '70', 'time': '71', 'template': '72', 'title': '73',
                         'tr': '74',
                         'track': '75', 'tt': '76', 'u': '77', 'ul': '78', 'var': '79', 'video': '7a', 'wbr': '7b',
                         '/!--...--': '7c', '/!DOCTYPE': '7d', '/a': '7e', '/abbr': '7f', '/acronym': '80',
                         '/address': '81',
                         '/applet': '82', '/area': '83', '/article': '84', '/aside': '85', '/audio': '86', '/b': '87',
                         '/base': '88',
                         '/basefont': '89', '/bdi': '8a', '/bdo': '8b', '/big': '8c', '/blockquote': '8d',
                         '/body': '8e',
                         '/br': '8f', '/button': '90', '/canvas': '91', '/caption': '92', '/center': '93',
                         '/cite': '94',
                         '/code': '95', '/col': '96', '/colgroup': '97', '/command': '98', '/datalist': '99',
                         '/dd': '9a',
                         '/del': '9b', '/details': '9c', '/dfn': '9d', '/dialog': '9e', '/dir': '9f', '/div': 'a0',
                         '/dl': 'a1',
                         '/dt': 'a2', '/em': 'a3', '/embed': 'a4', '/fieldset': 'a5', '/figcaption': 'a6',
                         '/figure': 'a7',
                         '/font': 'a8', '/footer': 'a9', '/form': 'aa', '/frame': 'ab', '/frameset': 'ac', '/h1': 'ad',
                         '/h2': 'ae',
                         '/h3': 'af', '/h4': 'b0', '/h5': 'b1', '/h6': 'b2', '/head': 'b3', '/header': 'b4',
                         '/hr': 'b5',
                         '/html': 'b6', '/i': 'b7', '/iframe': 'b8', '/img': 'b9', '/input': 'ba', '/ins': 'bb',
                         '/kbd': 'bc',
                         '/keygen': 'bd', '/label': 'be', '/legend': 'bf', '/li': 'c0', '/link': 'c1', '/main': 'c2',
                         '/map': 'c3',
                         '/mark': 'c4', '/menu': 'c5', '/meta': 'c6', '/meter': 'c7', '/nav': 'c8', '/noframes': 'c9',
                         '/noscript': 'ca', '/object': 'cb', '/ol': 'cc', '/optgroup': 'cd', '/option': 'ce',
                         '/output': 'cf',
                         '/p': 'd0', '/param': 'd1', '/pre': 'd2', '/progress': 'd3', '/q': 'd4', '/rp': 'd5',
                         '/rt': 'd6',
                         '/ruby': 'd7', '/s': 'd8', '/samp': 'd9', '/script': 'da', '/section': 'db', '/select': 'dc',
                         '/small': 'dd', '/source': 'de', '/span': 'df', '/strike': 'e0', '/strong': 'e1',
                         '/style': 'e2',
                         '/sub': 'e3', '/summary': 'e4', '/sup': 'e5', '/table': 'e6', '/tbody': 'e7', '/td': 'e8',
                         '/textarea': 'e9', '/tfoot': 'ea', '/th': 'eb', '/thead': 'ec', '/time': 'ed',
                         '/template': 'ee',
                         '/title': 'ef', '/tr': 'f0', '/track': 'f1', '/tt': 'f2', '/u': 'f3', '/ul': 'f4',
                         '/var': 'f5',
                         '/video': 'f6', '/wbr': 'f7'}

    def get_links(self, html: str) -> list:
        links = self.re_link.findall(html)
        return list(set(x[0] for x in links))

    def get_title(self, html: str) -> str:
        match = self.re_title_write.search(html)
        if match is None:
            match = self.re_title_tag.search(html)
        if match is None:
            return ""
        match = match.group(1)
        title = (match.strip("'\"") if match else "").replace("\n", " ")
        return title

    def tag_hash(self, tag: str) -> str:
        code = self.tag2code.get(tag, "00")
        return code

    def dom_tree(self, html: str) -> str:
        try:
            tags = self.re_tag.findall(html.lower())
        except:
            return ""
        return "".join([self.tag_hash(tag) for tag in tags])



if __name__ == '__main__':
    import requests

    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
    }
    ht = Html()
    html = requests.get("https://qq.com", headers=headers).text

    print(ht.get_links(html))

    print(ht.get_title(html))

    print(ht.dom_tree(html))
