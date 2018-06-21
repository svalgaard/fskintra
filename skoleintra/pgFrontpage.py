# -*- coding: utf-8 -*-

import config
import surllib
import semail
import re
import BeautifulSoup
import time

URL_SUFFIX = '/Index'

def skoleFrontpage():
    global div # FIXME
    # FIXME also do birthdays!
    assert(config.CHILD_PREFIX)

    url = config.CHILD_PREFIX + URL_SUFFIX

    config.log('Behandler forsiden %s' % url)
    data = surllib.skoleGetURL(url, asSoup=True, noCache=True)

    # find interesting main front page items
    for div in data.findAll('div', 'sk-news-item'):
        author = div.find('div', 'sk-news-item-author')
        body = div.findAll('div', 'sk-user-input')[0]
        msg = semail.Message(u'frontpage', body)

        msg.setTitle(body.text, True)
        msg.setMessageID(div['data-feed-item-id'])
        msg.setSender(author.span.text)

        author.span.extract() # remove author
        author.span.extract() # remove 'til'
        for tag in [
            author.span, # remove author
            author.span, # remove 'til'
            author.find('span', 'sk-news-item-and'), # ' og '
            author.find('a', 'sk-news-show-more-link')]:
            if tag:
                tag.extract()
        msg.setRecipient(author.text)

        # 19. jun. 2018 => 19-06-2018
        ds = div.find('div', 'sk-news-item-timestamp').text
        ds = time.strptime(ds, '%d. %b. %Y')
        msg.setDate(time.strftime('%d-%m-%Y', ds))

        semail.maybeEmail(msg)



if __name__ == '__main__':
    # test
    skoleFrontpage()
