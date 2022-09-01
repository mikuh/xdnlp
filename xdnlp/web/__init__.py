from xdnlp.web.simhash_utils import SimHash
from xdnlp.web.html import Html
from xdnlp.web.fetch_html import Browser
from xdnlp.web.utils import hamming_distance_array, is_valid_url, url2domain, top_domain, decode_image

sh = SimHash()
html = Html()
bs = Browser()

simhash = sh.simhash
simhash_array = sh.simhash_array
simhash_string = sh.simhash_string






__all__ = ['simhash', 'simhash_array', 'simhash_string', 'html', 'url2domain', 'top_domain', 'decode_image', 'bs']
