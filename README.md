# HTMLExtractor

Automatically find list items in a webpage with "class" and sub-tree similarity.

## USAGE
```
# parpare webpage
>>> import requests
>>> page = requests.get('https://search.jd.com/Search?keyword=iphone').content.decode('utf-8')

# find lists in the page automatically
>>> from ListExtractor import ListExtractor
>>> ex = ListExtractor(page)   # show extraction informations, with abstract texts 
List 1: 97 items
<div style="display:none">
    <a href="//club.jd.com/rank/655/e69c8de58aa1e68081e5baa6e5a5bd_2.html">
        服务态度好
    <a href="//club.jd.com/rank/655/e59381e8b4a8e580bce5be97e4bfa1e8b596_2.html">
        品质值得信赖
	...
------------------------------
List 0: 30 items
<ul class="gl-warp clearfix" data-tpl="3">
    <li class="gl-item" data-pid="5089273" data-sku="5089273" data-spu="5089273">
        < > ￥6688.00 Apple iPhone 8 Plus (A1864) 64GB 金色 移动联通电信4G手机 限时特惠，下单立减1000元，成交价5688元！勾选[保障服务][原厂保2年]，原厂延保更安心。更多活动 二手有售 62万+条评价 关注 京东Apple产品专营店 自营 满赠
    <li class="gl-item" data-pid="5089235" data-sku="5089253" data-spu="5089235">
        < > ￥8388.00 Apple iPhone X (A1865) 64GB 深空灰色 移动联通电信4G手机 购机限量送原装手机壳。勾选[保障服务][原厂保2年]获得AppleCare+全方位服务，原厂延保更安心。更多活动 二手有售 8.2万+条评价 关注 京东Apple产品专营店 自营 赠
    <li class="gl-item" data-pid="4586850" data-sku="4586850" data-spu="4586850">
        < > ￥2399.00 Apple iPhone 6 32GB 金色 移动联通电信4G手机 勾选[保障服务][原厂保2年]获得AppleCare+全方位服务，原厂延保更安心。更多活动 二手有售 38万+条评价 关注 京东Apple产品专营店 自营 满赠
	...
>>>  
>>> ex.GetResult()  # return List 0 as BeautifulSoup elements list
>>> ex.GetResult(3) # return List 3 as BeautifulSoup elements list (the estimated best one is List 0)

>>> ex.MakeSelector(0)   # return jQuery selector of List 0, return '' if failed
'ul.gl-warp.clearfix li.gl-item'
 
# can use a selector for pages with same structure, without duplicate discovering
# e.g. the new page may not have enough list elements to discover the list
>>> sel = ex.MakeSelector(0)
>>> page2 = requests.get('https://search.jd.com/Search?keyword=ipad').content.decode('utf-8')
>>> ex2 = ListExtractor(page2, selector=sel)   
```
