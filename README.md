# Weather Context

Weather context is a twitter bot that tweets the daily weather measured at Sydney Observatory Hill in its historical context. The data is from Bureau of Meteorology.

My favourite part of weather reports is when they give some context like "Hotest recorded August day" and I wanted to see more of that. When I started to look at the graphs I also noted the consistent upward trend and I wanted to explore that more and see how much the temperature has changed  in recent times (but I'm not a climate scientist and this bot in _[#Weather-context-does-not-prove-climate-change](#this-does-not-prove-climate-change)_).


## How it works
This twitterbot relies on 4 separate lambda functions:
* Update BOM Oberservation Observatory hills: get the __[daily weather observation](http://www.bom.gov.au/climate/dwo/IDCJDW2124.latest.shtml)__ for Observatory hill using the BOM API. This is only updated daily when the official numbers come out.
* Update BOM Oberservatory hills scraper: every hour it scrapes __[the latest Sydney Observations](http://www.bom.gov.au/nsw/observations/sydney.shtml)__ to find the currently recorded daily minimum and maximum.
* Generate temperate tweet: generates temperature tweets based on the minimum or maximum daily temperature.
* Send tweet: monitors the S3 bucket where tweets are stored. When a new one is created it is imediately tweeted


## Weather context does not prove climate change

Climate change is completely real, there is plenty of science on it. This twitter bot is not real science. It is only looking at single days of weather and in many ways not providing much actual context. It is only looking at Sydney, not considering weather patterns like El Niño or La Niña and a host of other factos that real climate scientist consider.

It is only meant as an interesting tool to show what the temperature has been in one specific place over the last 160 years.

## Future plans
* Add today in the violin plots
* Montly summary tweet
* Record days over the whole month (e.g. Hotest August day)
* Rainfall information