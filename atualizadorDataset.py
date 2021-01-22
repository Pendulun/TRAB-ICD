from bs4 import BeautifulSoup, element
import urllib
import pandas as pd
import numpy as np
import math
import time

pages = 19
rec_count = 0
num_results = 1000
sleep_time = 2.0


header = False
writeMode = 'a'

# Às vezes, dava um erro de acesso no meio da execução do script mas os jogos de alguns gêneros já
# haviam sido completamente analisados, logo, eu tinha que re-executar o script mas pegando apenas
# jogos a partir dos gêneros que não foram pegos e mudando o modo de escrita no arquivo
# para que houvesse a concatenação de dados no final do arquivo e não sobrescrita 
# Todos os gêneros:
# "Party","Music","Action","Action-Adventure",["Visual+Novel","Education","Fighting",
# "Misc","MMO",] já tinha feito com esses gêneros
genreList = ["Party","Music","Action","Action-Adventure","Visual+Novel",
 	"Education","Fighting","Misc","MMO","Platform","Adventure",
	"Board+Game","Puzzle","Racing","Role-Playing","Sandbox",
	"Shooter","Simulation","Sports","Strategy"]

urlhead = 'https://www.vgchartz.com/gamedb/?page='

	#Faltou o sales_eu
for genre in genreList:
	rank = []
	gname = []
	platform = []
	year = []
	genre_result = []
	critic_score = []
	user_score = []
	publisher = []
	developer = []
	sales_na = []
	sales_pal = []
	sales_jp = []
	sales_ot = []
	sales_gl = []
	print(str(genre))
	num_pages = 1
	urltail = '&console=&region=All&developer=&publisher=&genre='+ str(genre)
	urltail += '&boxart=Both&ownership=Both'
	urltail += '&results='+str(num_results) +'&order=Sales&showtotalsales=0&showtotalsales=1&showpublisher=0'
	urltail += '&showpublisher=1&showvgchartzscore=0&shownasales=1&showdeveloper=1&showcriticscore=1'
	urltail += '&showpalsales=0&showpalsales=1&showreleasedate=1&showuserscore=1&showjapansales=1'
	urltail += '&showlastupdate=0&showothersales=1&showgenre=1&sort=GL'
	surl = urlhead + str(1) + urltail

	r = urllib.request.urlopen(surl).read()
	firstSoup = BeautifulSoup(r, "html.parser")
	find = firstSoup.find("div", {"id":"generalBody"})
	"""
	print(find)
	print("---------------")
	print(find.table)
	print("---------------")
	print(find.table.tr)
	print("---------------")
	print(find.table.tr.th)
	"""
	resultsText = firstSoup.find("div", {"id":"generalBody"}).table.tr.th.string
	print(resultsText)
	results = resultsText[resultsText.find("(") + 1:resultsText.find(")")]
	results = int(results.replace(',',''))
	print(results)
	
	#Get the number of pages on genre results
	num_pages = results/num_results
	frac, integer = math.modf(num_pages)
	if(not (frac).is_integer()):
		num_pages = 1
	num_pages += int(integer)

	for page in range(1, num_pages + 1):
		time.sleep(sleep_time)
		print("Pagina: {}".format(str(page)))
		surl = urlhead + str(page) + urltail
		r = urllib.request.urlopen(surl).read()
		soup = BeautifulSoup(r, "html.parser")

		# vgchartz website is really weird so we have to search for
		# <a> tags with game urls
		# discard the first 10 elements because those
	    # links are in the navigation bar
		game_tags = list(filter(lambda x: x.attrs['href'].startswith('https://www.vgchartz.com/game/'),
			soup.find_all('a', href=True)))[10:]
		count=0
		for tag in game_tags:
			count += 1
			if(count%50 == 0):
				print("Jogo numero {}".format(count))
			# add name to list
			gname.append(" ".join(tag.string.split()))
			#print(f"{rec_count + 1} Fetch data for game {gname[-1]}")
			# get different attributes
			# traverse up the DOM tree
			#faltou para o sales_eu
			data = tag.parent.parent.find_all("td")
			rank.append(np.int32(data[0].string))
			platform.append(data[3].find('img').attrs['alt'])
			publisher.append(data[4].string)
			developer.append(data[5].string)
			critic_score.append(
				float(data[6].string) if
				not data[6].string.startswith("N/A") else np.nan)
			user_score.append(
				float(data[7].string) if
				not data[7].string.startswith("N/A") else np.nan)
			sales_na.append(
				float(data[9].string[:-1]) if
				not data[9].string.startswith("N/A") else np.nan)
			sales_pal.append(
				float(data[10].string[:-1]) if
				not data[10].string.startswith("N/A") else np.nan)
			sales_jp.append(
				float(data[11].string[:-1]) if
				not data[11].string.startswith("N/A") else np.nan)
			sales_ot.append(
				float(data[12].string[:-1]) if
				not data[12].string.startswith("N/A") else np.nan)
			sales_gl.append(
				float(data[8].string[:-1]) if
				not data[8].string.startswith("N/A") else np.nan)
			release_year = data[13].string.split()[-1]
			# different format for year
			if release_year.startswith('N/A'):
				year.append('N/A')
			else:
				if int(release_year) >= 80:
					year_to_add = np.int32("19" + release_year)
				else:
					year_to_add = np.int32("20" + release_year)
				year.append(year_to_add)
			genre_result.append(genre.replace('+',' '))

	#It saves the results so far for every genre as it can be tedius to it to fail mid processing
	print("Rank size: {}".format(len(rank)))
	print("Name size: {}".format(len(gname)))
	print("Platform size: {}".format(len(platform)))
	print("Year size: {}".format(len(year)))
	print("Genre size: {}".format(len(genre_result)))
	print("Critic Score size: {}".format(len(critic_score)))
	print("User score size: {}".format(len(user_score)))
	print("Publisher size: {}".format(len(publisher)))
	print("Developer size: {}".format(len(developer)))
	print("NA Sales: {}".format(len(sales_na)))
	print("PAL Sales: {}".format(len(sales_pal)))
	print("JP Sales: {}".format(len(sales_jp)))
	print("Other Sales: {}".format(len(sales_ot)))
	print("Global Sales: {}".format(len(sales_gl)))

	columns = {
		'Rank': rank,
		'Name': gname,
		'Platform': platform,
		'Year': year,
		'Genre': genre_result,
		'Critic_Score': critic_score,
		'User_Score': user_score,
		'Publisher': publisher,
		'Developer': developer,
		'NA_Sales': sales_na,
		'PAL_Sales': sales_pal,
		'JP_Sales': sales_jp,
		'Other_Sales': sales_ot,
		'Global_Sales': sales_gl
	}
	print(rec_count)
	df = pd.DataFrame(columns)
	print(df.columns)
	df = df[['Rank', 'Name', 'Platform', 'Year', 'Genre',
		'Publisher', 'Developer', 'Critic_Score', 'User_Score',
		'NA_Sales', 'PAL_Sales', 'JP_Sales', 'Other_Sales', 'Global_Sales']]
	df.to_csv("vgsales.csv", sep=",", encoding='utf-8', index=False, mode=writeMode, header=header)
	if(header):
		header=False
	if(writeMode == 'w'):
		writeMode = 'a'
