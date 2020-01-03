import scrapy, json, random

'''
Una query SPARQL sarebbe stata molto piu' veloce, ma sembra che alcuni link
(ad esempio i siti personali) non siano presenti nel database
'''

class ScraperDeputati(scrapy.Spider):
	name = 'ScraperDeputati'
	custom_settings = {'DOWNLOAD_DELAY': 1, 'RANDOMIZE_DOWNLOAD_DELAY': True}
	
	start_urls = ['http://www.camera.it/leg18/28?lettera='+i for i in list('ABCDEFGILMNOPQRSTUVZ')]
	
	def parse(self, response):
		list_ids_deputati = [d.split('idPersona=')[-1].split('&')[0] for d in 
			response.xpath('//div[@class="vcard"]/div[@class="fn"]/a/@href').extract()]
			
		for id_i in list_ids_deputati:
			yield scrapy.Request('http://www.camera.it/leg18/29?shadow_deputato={}&idLegislatura=18'.format(id_i),
				callback=self.parse_scheda_deputato, meta={'id_deputato': id_i})
				
	def parse_scheda_deputato(self, response):
		# Estraggo i dati anagrafici
		xpath_nome_partito = '//div[@class="datiDeputato"]/div[@class="nominativo"]/text()'
		nome_partito = response.xpath(xpath_nome_partito).extract_first().replace(u'\xa0', u' ')
		cognome_nome = nome_partito.split('-')[0].strip()
		sigla_partito = nome_partito.split('-')[1].strip()
		
		dict_out = {'id_deputato': response.meta['id_deputato'], 'cognome_nome': cognome_nome, 'sigla_partito': sigla_partito}
		
		# Estraggo i link social
		dict_counter_social = {}
		
		for elem_i in response.xpath('//ul[@class="social"]/li'):
			social_type_i = elem_i.xpath('@class').extract_first()
			social_link_i = elem_i.xpath('a/@href').extract_first()
			
			current_counter = dict_counter_social.get(social_type_i, 1)
			dict_counter_social[social_type_i] = current_counter+1
			
			dict_out[social_type_i + '_' + str(current_counter)] = social_link_i
		
		yield dict_out
