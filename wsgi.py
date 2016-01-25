#!/usr/bin/env python
#coding:utf-8
"""
  Author:   --<zhiyuan>--
  Purpose: 
  Created: 2014/3/28
"""
import os

virtenv = os.environ['OPENSHIFT_PYTHON_DIR'] + '/virtenv/'
virtualenv = os.path.join(virtenv, 'bin/activate_this.py')
try:
    execfile(virtualenv, dict(__file__=virtualenv))
except IOError:
    pass

import json
import logging
import urllib2
import uimodules

import tornado.web
import tornado.wsgi
import wsgiref.simple_server

from bs4 import BeautifulSoup

class SmallHandler(tornado.web.RequestHandler):
    #----------------------------------------------------------------------
    def get(self, q):
        url ='http://btdigg.org/search?info_hash=&q=%s'%q.encode('utf-8')
        try:    
            chunk = urllib2.urlopen(url,timeout=15).read()
            results = self.parse_info(chunk)
            error = None
        except BaseException, e:
            results = None
            error = str(e)
        if results and results is not str:
            self.render('smalllist.html', results=enumerate(results[:6]), error=error)
        else:
            self.render('smalllist.html', results=results, error=error)
    #----------------------------------------------------------------------
    def parse_info(self, chunk):
        """"""
        info = []
        keys = ['name','files','magnet','total_size','num_files','query','creation_date','updates','fack']
        soup = BeautifulSoup(chunk)
        posts = soup(attrs={"class":"torrent_name_tbl"})
        file_posts = soup(attrs={"class":"snippet"})
        for i, post in enumerate(posts):
            if i%2==0:
                values=[post.text]
                file_post = file_posts[i/2]
                [s.extract() for s in file_post('script')]
                [s.extract() for s in file_post('a')]
                try:
                    files = file_post.text.split("\n")
                except:
                    files = str(file_post).split("\n")[1:-1]
                files = filter(None, files)
                values.append(files)
            else:
                values.append(post.a['href'])
                for j in post.find_all(attrs={'class':"attr_val"}):
                    values.append(j.text)
                info.append(dict(zip(keys, values)))
        return info

class TestHandler(tornado.web.RequestHandler):
    #----------------------------------------------------------------------
    def get(self, q):
        url ='http://btdigg.org/search?info_hash=&q=%s'%q.encode('utf-8')
        try:    
            chunk = urllib2.urlopen(url,timeout=15).read()
            results = self.parse_info(chunk)
            results = json.dumps(results, ensure_ascii=False)
        except BaseException, e:
            results = str(e)
        self.write(results)
    #----------------------------------------------------------------------
    def parse_info(self, chunk):
        """"""
        info = []
        keys = ['name','magnet','total_size','num_files','query','creation_date','updates','fack']
        soup = BeautifulSoup(chunk)
        posts = soup(attrs={"class":"torrent_name_tbl"})
        for i, post in enumerate(posts):
            if i%2==0:
                [s.extract() for s in post('span')]
                [s.extract() for s in post('script')]
                values=[post.text]
            else:
                values.append(post.a['href'])
                for j in post.find_all(attrs={'class':"attr_val"}):
                    values.append(j.text)
                info.append(dict(zip(keys, values)))
        return info

class IndexHandler(tornado.web.RequestHandler):
    #----------------------------------------------------------------------
    def get(self):
        q = self.get_argument('q', '')
        page = self.get_argument('page', '1')
        try:
            page = int(page)
        except:
            page = 1
        url = 'http://btdigg.org/search?info_hash=&q=%s&p=%s'%(q.encode('utf-8'),page-1)
        try:    
            chunk = urllib2.urlopen(url,timeout=15).read()
            results = self.parse_info(chunk)
            results_count = results[-1][1]*10
            results.pop(-1)
            info = None
        except BaseException, e:
            results = None
            info = str(e)
        if results:
            self.render('index.html', results=enumerate(results), page=page, page_size=10, results_count=results_count, info=info)
        else:
            if not q: info = 'Hello Guaiguai, Welcome!'
            self.render('index.html', results=results, info = info)
    #----------------------------------------------------------------------
    def parse_info(self, chunk):
        """"""
        info = []
        keys = ['name','files','magnet','total_size','num_files','query','creation_date','updates','fack']
        soup = BeautifulSoup(chunk)
        posts = soup(attrs={"class":"torrent_name_tbl"})
        file_posts = soup(attrs={"class":"snippet"})
        pagers = soup(attrs={"class":"pager"})
        if pagers: 
            temp = pagers[0].td.next_sibling.text
            page = [int(i) for i in temp.split('/')]
        else:
            page = [0,0]
        for i, post in enumerate(posts):
            if i%2==0:
                [s.extract() for s in post('span')]
                [s.extract() for s in post('script')]
                values=[post.text]
                file_post = file_posts[i/2]
                [s.extract() for s in file_post('a')]
                [s.extract() for s in file_post('script')]
                try:
                    files = str(file_post).split("\n")[1:-1]
                except:
                    files = []
                files = filter(None, files)
                values.append(files)
            else:
                values.append(post.a['href'])
                for j in post.find_all(attrs={'class':"attr_val"}):
                    values.append(j.text)
                info.append(dict(zip(keys, values)))
        info.append(page)
        return info

settings = {
    "template_path": os.path.join(os.path.dirname(__file__), "templates"),
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    "ui_modules": uimodules
}

application = tornado.wsgi.WSGIApplication(
     handlers=[(r'/', IndexHandler),
               (r'/s/(.+)', SmallHandler),
               (r'/c/(.+)', TestHandler),],
    **settings
)

if __name__ == "__main__":
    server = wsgiref.simple_server.make_server('', 8000, application)
    server.serve_forever()
