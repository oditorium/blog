import tornado.ioloop
import tornado.web

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import numpy as np
from io import StringIO, BytesIO

import yaml
import json

class MainHandler(tornado.web.RequestHandler, arg=None):
	"""
	handles the requests to the root of the server (here a form that allows to 
	test posting YAML data)
	"""
	def get(self):
		self.write('<html><body><form action="/img/yaml" method="POST">'
			'<textarea name="data"></textarea><br>'
			'<input type="submit" value="Submit">'
			'</form></body></html>')

class ExplHandler(tornado.web.RequestHandler):
	"""
	renders a textbox containing example YAML data for testing the system
	"""
	
	def get(self, type1, arg=1):
		arg = float(arg)
		x = np.linspace(-10, 10, 1000)
		y = np.sin(x/arg)
		if type1 == "yaml": html = yaml.dump({"x":x.tolist(), "y":y.tolist()})
		else: html = json.dumps({"x":x.tolist(), "y":y.tolist()})
		html = type1+"<textarea>"+html+"</textarea>"
		self.write(html)
		
class ImgHandler(tornado.web.RequestHandler):
	"""
	core routine: receives a post request with the img data (yaml or json, depending on the
	type1 argument that is driven by the URL) and then renders a matplotlib image based on this,
	together with the correct content type
	"""
	
	def post(self, type1):	
		if type1 == "yaml": data = yaml.load(self.get_body_argument("data"))
		else: data = json.loads(self.get_body_argument("data"))
		x = data['x']
		y = data['y']
		plt.plot(x,y)
		
		io = BytesIO()
		plt.savefig(io, format='png')	
		plt.close()
		self.set_header("Content-Type", "image/png")
		self.write(io.getvalue())


application = tornado.web.Application([
	(r"/", MainHandler),
	(r"/in/(json|yaml)", MainHandler),
	(r"/img/(json|yaml)", ImgHandler),
	(r"/expl/(yaml|json)/(.*)", ExplHandler),
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
