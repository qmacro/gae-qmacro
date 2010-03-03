# mtgcardinfo
# Display all the cards mentioned in a Magic The Gathering article
# Scratched an itch - I print the articles out to read in the bath,
# and don't know the details of the cards that are mentioned!

# (c) DJ and Joseph Adams 2010

import re, os, logging
from google.appengine.api import urlfetch
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

GATHERER = 'http://gatherer.wizards.com'

class MainHandler(webapp.RequestHandler):

  def get(self):
    articleUrl = self.request.get('u')

    if articleUrl:

      # Get article
      try:
        result = urlfetch.fetch(articleUrl)

      except:
        self.response.out.write("Uh-oh, can't fetch %s" % articleUrl)
        return
    
      # Why parse the HTML for the title when I can get the browser's
      # DOM to give it to me? ;-)
      articleTitle = self.request.get('t')
      if articleTitle is None or articleTitle == "":
        articleTitle = articleUrl

      # Get unique list of cards linked in the article
      cards = []
      cards_upper = []
      for card in re.findall("autoCardWindow\('([\[\]\'\(\)\w]+?)'\)", result.content):
        if card.upper() not in cards_upper:
          cards_upper.append(card.upper())
          cards.append(card)

      # We want to output them in order, for easy searching
      cards.sort()
  
      # Send the response
      self.response.out.write("""
      <html><head><title>Cards: %s</title></head><body>
      <p><a href="/mtgcardinfo">Card details</a> for <a href="%s">%s</a></p>
      """ % (articleTitle, articleUrl, articleTitle))

      for card in cards:

        # Generate each card's image & detail URLs. See functions
        # in http://www.wizards.com/Assets/scripts/miscellaneous.js
        card = re.sub('_', '+', card)
        card = re.sub('\]', "&", card)
        card = re.sub('\[', "'", card)

        # Image URL
        idType = "multiverseid" if isinstance(card, int) else "name"
        cardImageUrl = GATHERER + "/Handlers/Image.ashx?"
        cardImageUrl += "type=card&%s=%s" % (idType, card)

        # Detail page URL
        detailUrl = GATHERER + "/Pages/Card/Details.aspx?name=%s" % card
  
        self.response.out.write("""
        <a style="color: white" href="%s"><img src="%s" alt="%s" /></a>\n
        """ % (detailUrl, cardImageUrl, card))

    # If we're not given a URL, show the about page
    else:
      path = os.path.join(os.path.dirname(__file__), 'templates', 'about.html')
      logging.info("** %s" % path)
      self.response.out.write(template.render(path, {'url': self.request.url}))


def main():
  application = webapp.WSGIApplication([
    ('/mtgcardinfo', MainHandler),
  ], debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
