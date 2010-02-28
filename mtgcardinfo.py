# mtgcardinfo
# Display all the cards mentioned in a Magic The Gathering article
# Scratched an itch - I print the articles out to read in the bath,
# and don't know the details of the cards that are mentioned!

# (c) DJ and Joseph Adams 2010

import re
from google.appengine.api import urlfetch

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

CARDS_PER_ROW = 4

class MainHandler(webapp.RequestHandler):

  def get(self):
    articleUrl = self.request.get('aurl')
    try:
      # Get article
      result = urlfetch.fetch(articleUrl)
      cards = []

      # Get unique list of cards linked in the article
      for card in re.findall("autoCardWindow\('(\w+)'\)", result.content):
        if card not in cards:
          cards.append(card)
      cards.sort()

      # Hack table together to show cards
      tab = "<table border='0'><tr>"
      cellCount = 0
      for card in cards:
        # Generate each card image's URL. See function OpenTip()
        # in http://www.wizards.com/Assets/scripts/miscellaneous.js
        card = re.sub('_', '+', card)
        idType = "multiverseid" if isinstance(card, int) else "name"
        cardImageUrl = "http://gatherer.wizards.com/Handlers/Image.ashx?"
        cardImageUrl += "type=card&%s=%s" % (idType, card)

        # Want CARDS_PER_ROW columns of card images
        # Four seems ideal for A4 printing, at this size
        if cellCount % CARDS_PER_ROW == 0: tab += "</tr><tr>"
        tab += "<td><img src='%s' /></td>" % cardImageUrl
        cellCount += 1
      tab += "</tr></table>"

      # Send the response
      self.response.out.write("""
      <p>Card details for <a href="%s">%s</a></p>%s
      """ % (articleUrl, articleUrl, tab))

    except:
      self.response.out.write("Uh-oh")



def main():
  application = webapp.WSGIApplication([('/mtgcardinfo', MainHandler)],
                                       debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
