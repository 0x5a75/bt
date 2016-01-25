#!/usr/bin/env python
#coding:utf-8
"""
  Author:   --<zhiyuan>--
  Purpose: 
  Created: 2014/3/28
"""
import math
import urllib
import urlparse

import tornado.web

def update_querystring(url, **kwargs):
    base_url = urlparse.urlsplit(url)
    query_args = urlparse.parse_qs(base_url.query)
    query_args.update(kwargs)
    for arg_name, arg_value in kwargs.iteritems():
        if arg_value is None:
            if query_args.has_key(arg_name):
                del query_args[arg_name]

    query_string = urllib.urlencode(query_args, True)     
    return urlparse.urlunsplit((base_url.scheme, base_url.netloc,
        base_url.path, query_string, base_url.fragment))

class Paginator(tornado.web.UIModule):
    """Pagination links display."""

    def render(self, page, page_size, results_count):
        pages = int(math.ceil(results_count / page_size)) if results_count else 0

        def get_page_url(page):
            # don't allow ?page=1
            if page <= 1:
                page = None
            return update_querystring(self.request.uri, page=page)
        def _pages_limit(page,pages):
            if pages<=10:
                return range(pages+1)[1:]
            elif page-5>0 and page+5<pages:
                return [1]+range(page-5+1,page+5+1)+[pages]
            elif page-5<=0:
                return range(1,11)+[pages]
            elif page+5>=pages:
                return [1]+range(pages+1)[-10:]
            else:pass

        next = page + 1 if page < pages else None
        previous = page - 1 if page > 1 else None
        pages_limit=_pages_limit(page, pages)
        
        return self.render_string('uimodules/pagination.html', page=page, pages=pages, next=next, pages_limit=pages_limit,
            previous=previous, get_page_url=get_page_url)
