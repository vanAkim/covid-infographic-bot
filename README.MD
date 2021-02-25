# Twitter bot displaying infographics about Covid-19 in France

**Purpose**: Post daily tweets about COVID-19 data of last 24h and 7days from public french database. Most of the content of the main tweets is shaped as infographics with emojis.  

**Process**:  
1. A python script, [run.py](https://github.com/vanAkim/covid-infographic-bot/blob/master/run.py) collects and transform data into a message intended to be tweeted with a dedicated account, [@InfographiCOVID](https://twitter.com/InfographiCOVID).  
2. In addition, each of these tweets are being responded to provided the data sources, which are (Santé Publique France)[https://www.santepubliquefrance.fr/] and [data.gouv.fr](https://www.data.gouv.fr/fr/).  
3. Finally, a Github Actions ([YAML config file](https://github.com/vanAkim/covid-infographic-bot/blob/master/.github/workflows/python-app.yml)) is set to execute the code each day at 8:30 UTC.
