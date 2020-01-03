import scrapy, json, random

'''
Una query SPARQL sarebbe stata molto piu' veloce, ma sembra che alcuni link
(ad esempio i siti personali) non siano presenti nel database
'''

class ScraperSenatori(scrapy.Spider):
	name = 'ScraperSenatori'
	custom_settings = {'DOWNLOAD_DELAY': 1, 'RANDOMIZE_DOWNLOAD_DELAY': True}
	
	start_urls = ['http://www.senato.it/leg/18/BGT/Schede/Attsen/Sen'+i+'.html' for i in list('abcdefgilmnopqrstuvz')]
	
	def parse(self, response):
		list_ids_senatori = response.xpath('//div[@class="linkSenatore"]/p/a/@href').extract()
		list_ids_senatori = [d for d in list_ids_senatori if 'sattsen' in d]
		list_ids_senatori = [int(d.split('id=')[-1].strip()) for d in list_ids_senatori]
	
		for id_i in list_ids_senatori:
			yield scrapy.Request('http://www.senato.it/leg/18/BGT/Schede/Attsen/{0:08d}.htm'.format(id_i),
				callback=self.parse_scheda_senatore, meta={'id_senatore': id_i})
				
	def parse_scheda_senatore(self, response):
		# Estraggo i dati anagrafici
		nome_cognome = response.xpath('//h1[@class="titolo"]/text()').extract_first().replace(u'\xa0', u' ')
		sigla_partito = response.xpath('//a[contains(@href, "tipodoc=sgrp")]/text()').extract_first()
		
		dict_out = {'id_senatore': response.meta['id_senatore'], 'nome_cognome': nome_cognome, 
			'sigla_partito': sigla_partito}
		
		# Estraggo i link social
		dict_counter_social = {}
		
		for elem_i in response.xpath('//ul[@class="composizione contatti"]/li/a'):
			social_type_i = [d.replace('cnt_', '') for d in elem_i.xpath('@class').extract_first().split(' ') if d != 'targetblank'][0]
			social_link_i = elem_i.xpath('@href').extract_first()
			
			current_counter = dict_counter_social.get(social_type_i, 1)
			dict_counter_social[social_type_i] = current_counter+1
			
			dict_out[social_type_i + '_' + str(current_counter)] = social_link_i
		
		yield dict_out
