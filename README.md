TPB_Filter
==========

Filter proxy for TPB to skip non- or badly seeded torrents

TPB is a great site, but especially for older torrents it can be very badly seeded, so you find pages and pages of torrents with no or 1 seeder, which really are pretty useless. This program starts a tiny proxy that filters out all the torrents that don't have a specified number of seeders.

As an added bonus it will also try to resolve links to preview images for a number of sites, so you dont have to click on them or open a new tab to see them.


Requirements
============

It needs python 2.7, CherryPy and BeautifulSoup4.

Usage
=====

Just run it. It starts a proxy on 8080, so just point your browser to localhost:8080 and have fun!

