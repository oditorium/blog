""" generates various displayhooks for iPython

this module does not really export any functions, but if it is imported
the iPython displayhooks are set to automatically display content

for example, if `im` is a PIL image, then simply doing

	im
	
will display it in the Notebook

source: http://nbviewer.ipython.org/gist/deeplook/5162445

"""


from io import BytesIO
from IPython.core import display
from PIL import Image

__version__    = "0.1"
__version_dt__ = "2014-09-20"


def display_pil_image(im):
   """Displayhook function for PIL Images, rendered as PNG."""

   b = BytesIO()
   im.save(b, format='png')
   data = b.getvalue()

   ip_img = display.Image(data=data, format='png', embed=True)
   return ip_img._repr_png_()


# register display func with PNG formatter:
png_formatter = get_ipython().display_formatter.formatters['image/png']
dpi = png_formatter.for_type(Image.Image, display_pil_image)


from io import BytesIO
from IPython.core import display
from reportlab.graphics import renderPM
from reportlab.graphics.shapes import Drawing

def display_reportlab_drawing(drawing):
   """displayhook function for ReportLab drawing, rendered as PNG"""

   buff = BytesIO()
   renderPM.drawToFile(drawing, buff, fmt='png', dpi=72)
   data = buff.getvalue()

   ip_img = display.Image(data=data, format='png', embed=True)
   return ip_img._repr_png_()


# register display func with PNG formatter:
png_formatter = get_ipython().display_formatter.formatters['image/png']
drd = png_formatter.for_type(Drawing, display_reportlab_drawing)
