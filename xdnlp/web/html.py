import re
from urllib import parse


class Html(object):

    def __init__(self):
        self.re_link = re.compile('"((http|ftp)s?://[a-zA-Z0-9_\-./]*?)"')

        self.re_title_tag = re.compile('>([^>]*?)</title>')
        self.re_title_write = re.compile('>\s*document\.title\s*=\s?([\S\s]*?);?\s*</script>')

        self.re_tag = re.compile("<(/?[a-z0-9]+?)[>\s]")
        self.re_image = re.compile(r'<img[^>]+?src="(.+?)"', re.S)
        self.re_content = re.compile(r'<script[\s\S]+?</script>|<[^>]+>|\s', re.S)

        self.re_wechat = re.compile(
            r'((微信|vx)[^a-zA-Z\d]{0,6}([a-zA-Z\d]{1}[a-zA-Z\d_-]{5,19}))|(([a-zA-Z\d]{1}[a-zA-Z\d_-]{5,19})[^a-zA-Z\d]{0,6}(微信|vx))',
            re.S)
        self.re_qq = re.compile(r'(qq[^\d]{0,4}(\d{8,12}))', re.S)
        self.re_phone = re.compile(r'[^\d|^](1(3\d|4[5-9]|5[0-35-9]|6[567]|7[0-8]|8\d|9[0-35-9])\d{8})[^\d|$]', re.S)

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

    def get_content(self, html: str, sep="") -> str:
        return self.re_content.sub(sep, html)

    def get_images(self, html: str, prefix=None) -> tuple:
        """
        Args:
            html: The original page
            prefix: the https + domain
        Returns:
            a tuple, first is image's links ,second is the base64 encode image
        """
        image_link = []
        image_base64 = []
        images = self.re_image.findall(html)
        for image in images:
            if image.startswith("data:image"):
                image_base64.append(image)
            elif prefix is not None:
                if image.startswith("//"):
                    image_link.append(prefix.split(":")[0] + ":" + image)
                else:
                    image_link.append(parse.urljoin(prefix, image))
            else:
                image_link.append(image)
        return image_link, image_base64

    def tag_hash(self, tag: str) -> str:
        code = self.tag2code.get(tag, "00")
        return code

    def dom_tree(self, html: str) -> str:
        try:
            tags = self.re_tag.findall(html.lower())
        except:
            return ""
        return "".join([self.tag_hash(tag) for tag in tags])

    def extract_contact(self, html: str, wechat=True, qq=True, phone=True) -> dict:
        content = self.get_content(html, " ").lower()
        contacts = {}
        if wechat:
            contacts["wechat"] = set()
            for x in self.re_wechat.findall(content):
                if x[2] and x[2] not in ('微信', 'vx'):
                    contacts["wechat"].add(x[2])
                elif x[1] and x[1] not in ('微信', 'vx'):
                    contacts["wechat"].add(x[1])
        if phone:
            contacts["phone"] = set([x[0] for x in self.re_phone.findall(content)])
        if qq:
            contacts["qq"] = set()
            for x in self.re_qq.findall(content):
                contacts["qq"].add(x[1])

        return contacts


if __name__ == '__main__':
    import requests

    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
    }
    ht = Html()
    html = requests.get("https://baidu.com", headers=headers).text

    print(ht.get_links(html))

    print(ht.get_title(html))

    print(ht.dom_tree(html))

    print(ht.get_images(html, "https://baidu.com"))

    print(ht.extract_contact(
        "导师微信： chenyue8870 武汉公司背景墙logo字体设计制作.武汉百阳广告电话：13476864737QQ：641173866湖北瑞丰科技HUBEI REFAN SCIENCE&TECHNOLOGY CO.LTD"))

    print(ht.get_content("""
<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <title>凯发k8国际_K8凯发国际官网</title>
    <meta http-equiv="X-UA-Compatible" content="IE=edge,Chrome=1" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=0">
    <meta name="format-detection" content="telephone=no,email=no,address=no">
    <meta property="og:url" content="http://www.91aiji.com/">
    <meta name="keywords" content="凯发k8国际,K8凯发国际" />
    <meta name="description" content="凯发k8国际是亚洲实力雄厚的一家线上游戏公司,提供丰富有趣的运动、彩票和角子游戏等产品,{核心关键词}已成为活跃在欧洲主流市场的在线娱乐平台。" /> 
    <link href="/templets/mb0106_f09/style/common.css?t=71465c" rel="stylesheet" media="screen" type="text/css">
    <link href="/templets/mb0106_f09/style/swiper.min.css?71465c" rel="stylesheet" media="screen" type="text/css" />
    <link href="/templets/mb0106_f09/style/animate.min.css?71465c" rel="stylesheet" media="screen" type="text/css" />
    <link href="/templets/mb0106_f09/style/style.css?71465c" rel="stylesheet" media="screen" type="text/css" />
    <link rel="shortcut icon" href="/templets/mb0106_f09/images/favicon.ico">
    <script type="text/javascript" src="/images/js/jquery.js?71465c"></script>
    <script type="text/javascript">var uipre = "z85756";var anim = "upbit";</script>
    <script type="text/javascript" src="/templets/mb0106_f09/ui/ui.js?71465c"></script>
    <script type="text/javascript" src="/templets/mb0106_f09/js/wow.min.js?71465c"></script>
    <script type="text/javascript" src="/templets/mb0106_f09/js/common.js?71465c"></script>

凯发k8国际
</head>
<body class="index">
  <script src='/index.php?act=api&aid=1' language='javascript'></script> <div class="z85756header">
    <div class="z85756main">
        <div class="logo">
            <h1><a href="http://www.91aiji.com/"><img src="https://img1.baidu.com/it/u=2004445936,3943264364&fm=253&fmt=auto&app=138&f=JPEG?w=230&h=164" alt="凯发k8国际_K8凯发国际官网"></a>
            </h1>
        </div>
        <div class="z85756navmenu">
            <ul class="z85756nav" lay-bar="disabled">
                <li class="z85756nav-item"><a href="http://www.91aiji.com/">首页</a></li>
                
                <li class="z85756nav-item"><a href='http://www.91aiji.com/kaifak8guojichanpinzhongxin/'  >凯发k8国际产品中心
                        </a> </li>
                <li class="z85756nav-item"><a href='http://www.91aiji.com/K8kaifaguojixinwenzhongxin/'  >K8凯发国际新闻中心
                        </a> </li>
                <li class="z85756nav-item"><a href='http://www.91aiji.com/guanyuwomen/'  >关于我们
                        </a> </li> </ul> </div> <div
                        class="search">
                        <ul>
                            <li>
                                <i class="z85756icon z85756icon-search "></i>
                                <div class="data_head_sear">
                                    <span class="z85756icon z85756icon-search "></span>
                                    <input type="text" placeholder="开始搜索">
                                </div>
                            </li>
                        </ul>
        </div>
    </div>
    <div class="icon_menu icon_r"><a class="i_menu z85756icon z85756icon-spread-left"></a><a
            class="i_close z85756icon z85756icon-close"></a></div>
    <div class="bg_hover"></div>
</div>
<!-- 占位盒子 -->
<div style="width: 100%;height: 95px; display: none;@media screen (max-width:1024px){
    display:block;
}"></div>



<script>
    $(function () {
        //遍历判断栏目是解决方案栏目，
        for (var i = 0; i < $('.z85756navmenu ul li dl .z85756nav-l').length; i++) {
            if ($('.z85756navmenu ul li dl .z85756nav-l').eq(i).children().length == 4) { //自定义内容长度==4
                //遍历子栏目
                var j = 0
                for (var index = 0; index < $('.z85756navmenu ul li dl .z85756nav-l').eq(i).siblings()
                    .children().length; index++) {
                    if (j > 3) {
                        j = 0
                    }
                    $('.z85756navmenu ul li dl .z85756nav-l').eq(i).children().eq(j).append($(
                        '.z85756navmenu ul li dl .z85756nav-l').eq(i).siblings().children().eq(
                        index).children())
                    j++
                }
            }
        }
        // 放大镜搜索  淡入淡出
        $('.z85756header .search i').on('click', function () {
            $('.z85756header .search .data_head_sear ').stop().slideToggle()
        })
        $('.z85756navmenu ul li').on('mouseenter', function () {
            $(this).siblings().children('a').css({
                opacity: '0.7'
            })
            $(this).children('a').css({
                opacity: '1'
            })
        })
        $('.z85756navmenu ul li').on('mouseleave', function () {
            $('.z85756navmenu ul li').children('a').css({
                opacity: '1'
            })
        })
    })
    //点击banner向下箭头
    $('.guanyuwomenGodown p').on('click', function () {
        $('html,body').animate({
            scrollTop: $('.swiper-container .swiper-slide').height()
        }, 500);
    })
</script>
  <div class="z85756container">
     <!--525-->
  <div class="z85756row z85756main z85756in3 wow animated zoomIn">
    <div class="z85756col-md6">
      <img src="/templets/mb0106_f09/images/litp_6.png" alt="">
    </div>
    <div class="z85756col-md6">
      <h2>关于我们</h2>
      <span>
 
      公司搬家拆装队伍随时等候您的差追，为您提供优质的家居拆装服务；公司搬家拆装队伍均配有拆装工具箱, 里面包含各种家具拆装所有工具,让悠尊享高效、安全的拆装服务；公司建立了一整套家居拆装培训体系，培养了一 大批专业拆装人员,让您尊享专业化家居拆装服务。
<!--diy3-->
      </span>
      <h2>——</h2>
    </div>
  </div>
     <!--505-->
<div class="product w100">

            <div class="z85756row">
                <div class="z85756col-md6">
                    <div class="pdtLeft bcg1">
                        <div class="pdtFont">
                            <div class="pdtTle">凯发k8国际_K8凯发国际官网<i></i></div>
                            <ul class="pdtList mt30">
                                <li><a href="#"></a></li>
<li><a href="#">凯发k8国际_K8凯发国际官网</a></li>

                            </ul>
                            <a href="">
                                <div class="pdtMore">
                                    more
                                </div>
                            </a>
                        </div>
                    </div>
                </div>
                <div class="z85756col-md6">
                    <div class="pdtLeft bcg2">
                        <div class="pdtFont">
                            <div class="pdtTle">凯发k8国际_K8凯发国际官网<i></i></div>
                            <ul class="pdtList mt30">
                                <li><a href="#"></a></li>
<li><a href="#">凯发k8国际_K8凯发国际官网</a></li>


                            </ul>
                            <a href="">
                            <div class="pdtMore bcec6">
                                more
                            </div>
                            </a>
                        </div>
                    </div>
                </div>
            </div>

        </div>
     
             <div class="z85756main content_1 w100">
            <div class="z85756row more">
                <div class="swiper-container5 swiper">
                    <div class="swiper-wrapper">
                        <div class="swiper-slide">
                            <div class="z85756col-md12">
                                <div class="news_list_item_line">
                                    <div class="news_list_item_inner">
                                        <div class="news_list_img_box">
                                            <div class="news_list_img"></div>
                                        </div>
                                        <div class="news_list_item_content">
                                            <div class="news_list_item_header">
                                                <div class="img">
                                                    <img src="/images/defaultpic.gif" alt="">
                                                </div>
                                                <h4 class="news_list_item_title"><a href="http://www.91aiji.com/K8kaifaguojixinwenzhongxin/144366.html" title="凯发k8国际 米哈游旗下虚构偶像鹿鸣B站直播首秀半小时获66万人有观看">凯发k8国际 米哈游旗下虚构偶像鹿鸣B站直播首秀半小时获66万人有观看</a></h4>
                                                <!-- <span class="news_list_item_date">2022-07-17</span> -->
                                            </div>
                                            <div class="news_list_item_summery des">7月15日晚，米哈游旗下虚构偶像鹿鸣在B站开启了初次直播。开播后该直播间坐窝冲上B站直播热点总榜，数据知道，本场半小时的直播统统迷惑了66万人前来有观看。当今，鹿鸣在B站已领有14</div>
                                            <!-- <div class="news_list_item_group"><a href="http://www.91aiji.com/K8kaifaguojixinwenzhongxin/" title="凯发k8国际 米哈游旗下虚">K8凯发国际新闻中心</a></div> -->
                                        </div>
                                    </div>
                                    <a href="http://www.91aiji.com/K8kaifaguojixinwenzhongxin/144366.html" class="news_list_item_link"></a>
                                </div>
                                <div class="news_list_parting_line jz_parting_line"></div>
                            </div>
                        </div>
<div class="swiper-slide">
                            <div class="z85756col-md12">
                                <div class="news_list_item_line">
                                    <div class="news_list_item_inner">
                                        <div class="news_list_img_box">
                                            <div class="news_list_img"></div>
                                        </div>
                                        <div class="news_list_item_content">
                                            <div class="news_list_item_header">
                                                <div class="img">
                                                    <img src="/uploads/allimg/220717/1_0GG34P3c02.png" alt="">
                                                </div>
                                                <h4 class="news_list_item_title"><a href="http://www.91aiji.com/K8kaifaguojixinwenzhongxin/144367.html" title="凯发k8国际 第三届大众Mini/Micro LED走漏本事周凯旋举办 多家上市公司高管发言 华为和小米也来了">凯发k8国际 第三届大众Mini/Micro LED走漏本事周凯旋举办 多家上市公司高管发言 华为和小米也来了</a></h4>
                                                <!-- <span class="news_list_item_date">2022-07-17</span> -->
                                            </div>
                                            <div class="news_list_item_summery des">记者 陈霞昌 由中国电子视像行业协会Mini/Micro LED走漏产业分会（CMMA）涵养，SciLinks Group垄断的“2022第三届大众Mini/Micro LED走漏本事周(Global Mini/Micro LED TechDays)”于 2022年7月13-14日在深圳举办。本</div>
                                            <!-- <div class="news_list_item_group"><a href="http://www.91aiji.com/K8kaifaguojixinwenzhongxin/" title="凯发k8国际 第三届大众M">K8凯发国际新闻中心</a></div> -->
                                        </div>
                                    </div>
                                    <a href="http://www.91aiji.com/K8kaifaguojixinwenzhongxin/144367.html" class="news_list_item_link"></a>
                                </div>
                                <div class="news_list_parting_line jz_parting_line"></div>
                            </div>
                        </div>
<div class="swiper-slide">
                            <div class="z85756col-md12">
                                <div class="news_list_item_line">
                                    <div class="news_list_item_inner">
                                        <div class="news_list_img_box">
                                            <div class="news_list_img"></div>
                                        </div>
                                        <div class="news_list_item_content">
                                            <div class="news_list_item_header">
                                                <div class="img">
                                                    <img src="/images/defaultpic.gif" alt="">
                                                </div>
                                                <h4 class="news_list_item_title"><a href="http://www.91aiji.com/kaifak8guojichanpinzhongxin/144350.html" title="凯发k8国际 上海环境动力来回所运行碳价钱指数开发职责 将为阛阓提供更丰富碳金融居品">凯发k8国际 上海环境动力来回所运行碳价钱指数开发职责 将为阛阓提供更丰富碳金融居品</a></h4>
                                                <!-- <span class="news_list_item_date">2022-07-17</span> -->
                                            </div>
                                            <div class="news_list_item_summery des">(严曦梦记者宋薇萍)7月16日下昼，2022中国海外碳来回大会在上海举办。会上，上海环境（601200）动力来回所(以下简称“上海环交所”)晓示运行碳价钱指数开发职责。在上海证券来回所的接济下</div>
                                            <!-- <div class="news_list_item_group"><a href="http://www.91aiji.com/kaifak8guojichanpinzhongxin/" title="凯发k8国际 上海环境动力">凯发k8国际产品中心</a></div> -->
                                        </div>
                                    </div>
                                    <a href="http://www.91aiji.com/kaifak8guojichanpinzhongxin/144350.html" class="news_list_item_link"></a>
                                </div>
                                <div class="news_list_parting_line jz_parting_line"></div>
                            </div>
                        </div>
<div class="swiper-slide">
                            <div class="z85756col-md12">
                                <div class="news_list_item_line">
                                    <div class="news_list_item_inner">
                                        <div class="news_list_img_box">
                                            <div class="news_list_img"></div>
                                        </div>
                                        <div class="news_list_item_content">
                                            <div class="news_list_item_header">
                                                <div class="img">
                                                    <img src="/uploads/allimg/220717/1_0GG34J91c9.png" alt="">
                                                </div>
                                                <h4 class="news_list_item_title"><a href="http://www.91aiji.com/K8kaifaguojixinwenzhongxin/144357.html" title="K8凯发国际 《魔兽寰宇》巨龙期间建设需求大幅提高，最低 3G 显存的 DX12 显卡">K8凯发国际 《魔兽寰宇》巨龙期间建设需求大幅提高，最低 3G 显存的 DX12 显卡</a></h4>
                                                <!-- <span class="news_list_item_date">2022-07-17</span> -->
                                            </div>
                                            <div class="news_list_item_summery des">7月16日音尘，暴雪如故告示，大型多人在线变装璜演游戏《魔兽寰宇》的下一个贵寓片“巨龙期间”现已敞开预购以及闭塞Alpha测试，并将于本年晚些期间推出。 “巨龙期间”是《魔兽寰宇》</div>
                                            <!-- <div class="news_list_item_group"><a href="http://www.91aiji.com/K8kaifaguojixinwenzhongxin/" title="K8凯发国际 《魔兽寰宇》">K8凯发国际新闻中心</a></div> -->
                                        </div>
                                    </div>
                                    <a href="http://www.91aiji.com/K8kaifaguojixinwenzhongxin/144357.html" class="news_list_item_link"></a>
                                </div>
                                <div class="news_list_parting_line jz_parting_line"></div>
                            </div>
                        </div>
<div class="swiper-slide">
                            <div class="z85756col-md12">
                                <div class="news_list_item_line">
                                    <div class="news_list_item_inner">
                                        <div class="news_list_img_box">
                                            <div class="news_list_img"></div>
                                        </div>
                                        <div class="news_list_item_content">
                                            <div class="news_list_item_header">
                                                <div class="img">
                                                    <img src="/uploads/allimg/220717/1_0GG34I92363.png" alt="">
                                                </div>
                                                <h4 class="news_list_item_title"><a href="http://www.91aiji.com/kaifak8guojichanpinzhongxin/144349.html" title="凯发k8国际 助力结束“双碳”成见 我国核电安全有序发展迎来“窗口期”">凯发k8国际 助力结束“双碳”成见 我国核电安全有序发展迎来“窗口期”</a></h4>
                                                <!-- <span class="news_list_item_date">2022-07-17</span> -->
                                            </div>
                                            <div class="news_list_item_summery des">北京7月16日电 （记者杜燕飞）刻下，我国核电正迎来安全有序发展“窗口期”。7月14日、15日，国度电投海阳核电二期工程暨900兆瓦远距离跨区域核能供热工程、华能海南昌江核电二期核岛装</div>
                                            <!-- <div class="news_list_item_group"><a href="http://www.91aiji.com/kaifak8guojichanpinzhongxin/" title="凯发k8国际 助力结束“双">凯发k8国际产品中心</a></div> -->
                                        </div>
                                    </div>
                                    <a href="http://www.91aiji.com/kaifak8guojichanpinzhongxin/144349.html" class="news_list_item_link"></a>
                                </div>
                                <div class="news_list_parting_line jz_parting_line"></div>
                            </div>
                        </div>

                    </div>
                    <div class="swiper-button-next"></div>
                    <div class="swiper-button-prev"></div>
                </div>
                <div class="z85756col-md12">
                    <a href="" class="look">More</a>
                </div>
            </div>
        </div>

    <script type="text/javascript" src="/templets/mb0106_f09/images/swiper.js?71465c"></script>
     
      
  </div>
  <div class="z85756footer">
  <div class="solve">
    <div class="z85756triangle-top tgcolor"></div>
    <div class="z85756triangle-bottom"></div>
  
          <div class="z85756main">
              <div class="z85756row">
                  <div class="z85756col-md12">
                      <div class="heart">
  
                      </div>
                      <h1>创新解决方案，促进人类健康</h1>
                  </div>
              </div>
          </div>
  
  
  
  
      </div>
  <div id="back-top" class="hid">
    <div class="back_top_content">
        <div class="back_top_system">
            <div class="svg_0"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48"><title>回到顶部</title> <rect width="48" height="48" rx="24" ry="24" fill="#63d3fc"></rect> <path d="M31.71,26.3l-7-7a1,1,0,0,0-1.4,0l-7,7a1,1,0,0,0,1.4,1.4L24,21.39l6.31,6.31a1,1,0,0,0,1.4-1.4Z" fill="#fff" fill-rule="evenodd"></path></svg></div>
        </div>
    </div>
</div>
<div>
  <div class="z85756triangle-bottom footer_bottom"></div>
  <div class="z85756triangle-top footer_top"></div>
</div>

    <div class="z85756main"><div class="z85756row footerserver">
        <div class="z85756col-md4">
          <dl>
            <dt>服务热线</dt>
            <dd>官方网站：www.365jz.com</dd>
            <dd>工作时间：周一至周六（09：00-18：00）</dd>
        </dl>
        </div>
        <div class="z85756col-md4">
          <dl>
            <dt>联系我们</dt>
            <dd>QQ：2852320325</dd>
            <dd>邮箱：w365jzcom@qq.com</dd>
            <dd>地址：武汉东湖新技术开发区光谷大道国际企业中心</dd>
        </dl>
        </div>
		<div class="z85756col-md4">
          <dl>
            <dt>关注公众号</dt>
            <dd><img width="100" src="/images/weixin.jpg" style="display: inline-block;"></dd>
        </dl>
        </div>
    </div>
	<div class="z85756flink">
		友情链接：<li><a href="http://www.syjtbg.com">米乐体育ios_米乐体育app登录</a></li><li><a href="http://www.hrgpcb.com">ob真人厅_OB欧宝真人官方网站</a></li><li><a href="http://www.octangel.com">尊龙手机客户端app_尊龙新版手机app</a></li><li><a href="http://www.houbaotech.com">am8亚美app_亚美am8官网app</a></li><li><a href="http://www.thefishingportal.com">雷泽电竞_雷泽体育_雷泽体育电竞官网</a></li><div class="clear"></div>
		</div>
	</div>

<div class="footerc">
    <p>Powered by <a href="http://www.91aiji.com//" target="_blank"><strong>凯发k8国际_K8凯发国际官网</strong></a> <a href="http://www.91aiji.com/sitemap.xml" target="_blank">RSS地图</a> <a href="http://www.91aiji.com/sitemap.html" target="_blank">HTML地图</a></p>
    <p><script>
var _hmt = _hmt || [];
(function() {
  var hm = document.createElement("script");
  hm.src = "https://hm.baidu.com/hm.js?d84949eb65845a7726c8014b3e1404e6";
  var s = document.getElementsByTagName("script")[0]; 
  s.parentNode.insertBefore(hm, s);
})();
</script>
K8凯发国际 <br />凯发k8国际_K8凯发国际官网-凯发k8国际_K8凯发国际官网	</p>
  <div class="clear"></div>
</div>
</div>

</body>
</html>"""))
