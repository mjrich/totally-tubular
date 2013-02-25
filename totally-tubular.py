#!/usr/bin/env python
import gdata.youtube.service
import gdata.alt.appengine
import os
import webapp2
import jinja2
import json
from urllib2 import urlopen

yt_service = gdata.youtube.service.YouTubeService()
yt_service.ssl = True
gdata.alt.appengine.run_on_appengine(yt_service)

#Code from http://code.activestate.com/recipes/498181-add-thousands-separator-commas-to-formatted-number/
def splitthousands(s, sep=','):  
    if len(s) <= 3: return s  
    return splitthousands(s[:-3], sep) + sep + s[-3:]


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)
		
	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)
		
	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

class SearchHandler(Handler):

	def render_form(self, countryval="", categoryval="", feedval="", numval="", timeval=""):
		self.render('main.html', countryval=countryval, categoryval=categoryval, feedval=feedval, numval=numval, timeval=timeval)
	
	def get(self):
		self.render_form()

  	def post(self):
		user_country = self.request.get('country')
		if user_country == "All":
			user_country = ""
		else: 
			user_country += '/'
		user_category = self.request.get('category')
		if user_category == "All":
			user_category = ""
		else:
			user_category = "_" + user_category
		user_feed = self.request.get('feed')
		user_number = self.request.get('number')
		user_time = self.request.get('time')

		uri = 'https://gdata.youtube.com/feeds/api/standardfeeds/%s%s%s?&time=%s&v=2&max-results=%s' % (user_country, user_feed, user_category, user_time, user_number)
		videos = yt_service.GetYouTubeVideoFeed(uri)
		video_list = []
		for index, entry in enumerate(videos.entry):
			try:
				video_list += [{'index':str(index + 1) , 'published':entry.published.text , 'updated':entry.updated.text , 'uploader':entry.media.credit.text , 'title':entry.title.text.decode('utf-8').replace('|',' ') , 'category':entry.media.category[0].text , 'length':entry.media.duration.seconds , 'rating':(float(entry.rating.average)/5*100) , 'comments':splitthousands(entry.comments.feed_link[0].count_hint) , 'numraters':entry.rating.num_raters , 'url':entry.media.player.url , 'vidcode':entry.media.player.url[32:43], 'views':splitthousands(entry.statistics.view_count)}]
			except:
				pass

		
		country = user_country[:2]

		alexa_uri = 'https://api.scraperwiki.com/api/1.0/datastore/sqlite?format=jsondict&name=alexa-country-ranks&query=select%20*%20from%20%60swdata%60%20where%20country%3D' + '\''+  country + '\''+ '%20limit%205'
		j = urlopen(alexa_uri)
		alexa_results = json.load(j)

		country = user_country.replace('/','-') 

		global alexa_results
		global video_list
		global uri
		global country


		self.redirect("/result")

class ResultHandler(Handler):

	def render_result(self, video_list="", uri="", country="", alexa_results=""):
		self.render('result.html', video_list=video_list, uri=uri, country=country, alexa_results=alexa_results)
	
	def get(self):
		self.render_result(video_list,uri, country, alexa_results)


app = webapp2.WSGIApplication([(r'/', SearchHandler),
			       (r'/result', ResultHandler)],
                              debug=False)
