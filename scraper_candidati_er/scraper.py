import scrapy

class ScraperCandidatiER(scrapy.Spider):
	name = 'ScraperCandidatiER'
	
	def start_requests(self):
		for circ in ['bologna', 'piacenza', 'parma', 'reggioemilia', 'rimini', 'forli-cesena', 'ferrara', 'modena', 'ravenna']:
			yield scrapy.Request(
				'https://www.regione.emilia-romagna.it/elezioni/regionali-2020/candidati-e-liste/{}'.format(circ),
				callback=self.parse, meta={'circ': circ}
			)

	def parse(self, response):
		list_liste = response.xpath('//div[contains(@class, "tile-text") and contains(@class, "tileBody")]/p/img/@title').extract()
		list_tables = response.xpath('//div[contains(@class, "tile-text") and contains(@class, "tileBody")]/table[contains(@class, "table-bordered") and contains(@class, "table-striped")]/tbody')
		
		for lista_i, table_i in zip(list_liste, list_tables):
			for candidato_i in table_i.xpath('./tr[position() >= 2]'):
				yield dict(zip(
					['nome_cognome', 'sesso', 'data_nascita', 'luogo_nascita'] + ['lista', 'circoscrizione'], 
					candidato_i.xpath('td/text()').extract() + [lista_i.strip(), response.meta['circ']]
				))
