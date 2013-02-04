#!/usr/bin/env python
import gdata.youtube.service
import gdata.alt.appengine
import os
import webapp2
import jinja2

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

	def render_form(self, countryval="", categoryval="", feedval="", numval=""):
		self.render('main.html', countryval=countryval, categoryval=categoryval, feedval=feedval, numval=numval)
	
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

		uri = 'https://gdata.youtube.com/feeds/api/standardfeeds/%s%s%s?&v=2&max-results=%s' % (user_country, user_feed, user_category, user_number)
		videos = yt_service.GetYouTubeVideoFeed(uri)
		video_list = []
		for index, entry in enumerate(videos.entry):
			try:
				video_list += [{'index':str(index + 1) , 'published':entry.published.text , 'updated':entry.updated.text , 'uploader':entry.media.credit.text , 'title':entry.title.text.decode('utf-8').replace('|',' ') , 'category':entry.media.category[0].text , 'length':entry.media.duration.seconds , 'rating':(float(entry.rating.average)/5*100) , 'comments':splitthousands(entry.comments.feed_link[0].count_hint) , 'numraters':entry.rating.num_raters , 'url':entry.media.player.url , 'vidcode':entry.media.player.url[32:43], 'views':splitthousands(entry.statistics.view_count)}]
			except:
				pass

		global video_list


		self.redirect("/result")

class ResultHandler(Handler):
	#def get(self):
	#	self.write("List: %s" % (video_list))

	def render_result(self, video_list=""):
		self.render('result.html', video_list=video_list)
	
	def get(self):
		self.render_result(video_list)

	#add CSV output from results page.

app = webapp2.WSGIApplication([(r'/', SearchHandler),
			       (r'/result', ResultHandler)],
                              debug=True)