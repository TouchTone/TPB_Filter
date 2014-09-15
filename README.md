TPB_Filter
==========

Filter proxy for TPB to skip non- or badly seeded torrents

TPB is a great site, but especially for older torrents it can be very badly seeded, so you find pages and pages of torrents with no or 1 seeder, which really are pretty useless. This program strats a tiny proxy that filters out all the torrents that don't have a specified number of seeders.

Requirements
============

It needs python 2.7, CherryPy and BeautifulSoup4.

Usage
=====

Just run it. It starts a proxy on 8080, so just point your browser to localhost:8080 and have fun!

