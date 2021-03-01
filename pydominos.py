import os
import sys
import datetime
import time
import struct
import argparse
import csv
import json
import requests
from bs4 import BeautifulSoup as Soup

OrderType = {
	'pickup': 0,
	'delivery': 1,
}

class DominosAPI:

	def __init__(self, countryCode = None, storeNo = None, culture = None):
		self.base = "https://dpe-prod-services-apigateway2-weu.azurewebsites.net/"
		self.s = requests.Session()
		self.countryCode = "NL"
		self.storeNo = str(30561)
		self.showSecretMenus = True
		self.orderTime = None
		self.culture = "en"

		if countryCode:
			self.countryCode = countryCode

		if storeNo:
			self.storeNo = str(storeNo)

		if culture:
			self.culture = culture

	def Products(self, countryCode=None, storeNo=None, productCode=None, culture=None):

		if not countryCode:
			countryCode = self.countryCode

		if not storeNo:
			storeNo = self.storeNo

		if not productCode:
			productCode = self.productCode

		if not culture:
			culture = self.culture

		response = self.s.get(self.base+countryCode+"/menus/"+storeNo+"/products/"+productCode+"/"+culture)

		return json.loads(response.content)


	def AllProducts(self, countryCode=None, culture=None, storeNo=None):
		
		if not countryCode:
			countryCode = self.countryCode

		if not culture:
			culture = self.culture

		if not storeNo:
			storeNo = self.storeNo

		response = self.s.get(self.base+"/products/forstore?country="+countryCode+"&culture="+culture+"&storeNo="+storeNo)

		return json.loads(response.content)

	def Prices(self, countryCode=None, culture=None, productCode=None, storeNo=None):

		if not countryCode:
			countryCode = self.countryCode

		if not culture:
			culture = self.culture

		if not storeNo:
			storeNo = self.storeNo

		formData = {
			'productCode':productCode,
			'storeNo':storeNo
		}

		response = self.s.post(self.base+"/"+countryCode+"/prices/"+culture, json=formData)

		return json.loads(response.content)

	def Stores(self, countryCode=None, culture=None, storeNo=None):

		if not countryCode:
			countryCode = self.countryCode

		if not culture:
			culture = self.culture

		if not storeNo:
			storeNo = self.storeNo

		response = self.s.get(self.base+"/"+countryCode+"/stores/"+storeNo+"?culture="+culture)

		return json.loads(response.content)

	def StoresByRegion(self, countryCode=None, region=None):

		if not countryCode:
			countryCode = self.countryCode
			
		response = self.s.get(self.base+"/"+countryCode+"/stores/all?region="+region)

		return json.loads(response.content)

	def Menus(self):
		pass

	def Varieties(self):
		pass

	def AllVarieties(self):
		pass

	def VoucherMenus(self):
		pass

	def WebVouchers(self, countryCode=None, culture=None, storeNo=None):
		
		if not countryCode = None:
			countryCode = self.countryCode

		if not culture:
			culture = self.culture
			
		if not storeNo:
			storeNo = self.storeNo

		response = self.s.get(self.base+"/"+countryCode+"/webvouchers/"+storeNo+"/"+culture)
		return json.loads(response.content)
	
	def Streets(self):
		pass

	def Suburbs(self):
		pass

	def StoreOrderTimes(self):
		pass

	def StoreCongestion(self):
		pass

	def StoreOrderCapacity(self):
		pass

	def OffersForLocation(self):
		pass

	def OffersForStoreTradingDate(self):
		pass

	def OffersBetweenDates(self):
		pass

	def RecentOrder(self):
		pass

	def OrderStatus(self):
		pass

	def OrderStatusInfo(self):
		pass

	def StatusTime(self):
		pass

	def PaymentMethods(self):
		pass

	def QuickOrderSummary(self):
		pass

	def CustomerTags(self):
		pass

	def AsapOrderSummary(self):
		pass

	def PriceProduct(self):
		pass

	def StoresWithLanguage(self):
		pass

	def MenuPage(self):
		pass

class DominosWeb:
	
	def __init__(self, orderType=None):
		self.base = "https://bestellen.dominos.nl"
		self.s = requests.Session()
		self.viewBag = []
		self.orderType = orderType
		self.api = DominosAPI('NL',str(30561), 'en')

	def SetOrderType(self):
		
		suffix = "/eStore/nl/OrderTimeNowOrLater/Delivery"
		
		if self.orderType == OrderType['pickup']:
			suffix = "/eStore/nl/OrderTimeNowOrLater/Pickup"
		
		elif self.orderType != OrderType['delivery']:
			raise Exception('Invalid OrderType')

		self.viewBag.append(Soup(self.s.get(self.base+suffix).text, "html.parser"))

	def ProvideCustomerDetails(self):
		
		if self.orderType == OrderType['pickup']:
			self.ProvidePickupDetails()

		elif self.orderType == OrderType['delivery']:
			self.ProvideDeliveryDetails()

		else:
			raise Exception('Invalid OrderType')

	def ProvidePickupDetails(self):
		pass

	def ProvideDeliveryDetails(self):
		
		page = self.viewBag[-1]
		form = page.find("form", {'id':'delivery-details'})
		

		while True:
			
			formData = {}
			
			# Get form options
			for inputElement in form.find_all("input"):
				if "name" in inputElement.attrs and "value" in inputElement.attrs:
					formData[inputElement['name']] = inputElement['value']

			# Prepare form
			for k in formData.keys():
				if not formData[k]:
					formData[k] = input(k+": ")

			# Post
			response = self.s.post(self.base+form['action'], data=formData, allow_redirects=True)

			if response.status_code != 200:
				raise Exception("Failed to set orderType")

			if response.url == self.base+"/eStore/nl/DeliverySearch/AllDetails":
				self.viewBag.append(Soup(response.text, "html.parser"))
				break
			else:
				print("Please fill in the form as required!")

		page = self.viewBag[-1]
		form = page.find('form', {'action':'/eStore/nl/CustomerDetails/SpecifyDeliveryAddress'})
		
		results = form.find_all('button', {'class':'store-result'})
		if not len(results):
			raise Exception('Failed to find address')

		button = results[-1]

		formData = {}
		# Get form options
		for inputElement in form.find_all("input"):
			if "name" in inputElement.attrs and "value" in inputElement.attrs:
				formData[inputElement['name']] = inputElement['value']
		
		print("Will deliver to:", button.text)
		response = self.s.post(self.base+form['action'], data=formData, allow_redirects=True)

		if response.status_code != 200:
				raise Exception("Failed to SpecifyDeliveryAddress")

		self.viewBag.append(Soup(response.text, "html.parser"))

	def SpecifyOrderTime(self):
		
		page = self.viewBag[-1]
		form = page.find('form', {'action':'/eStore/nl/OrderTime/Submit'})

		formData = {}
		
		# Get form options
		for inputElement in form.find_all("input"):
			if "name" in inputElement.attrs and "value" in inputElement.attrs:
				formData[inputElement['name']] = inputElement['value']

		for inputElement in form.find_all("select"):
			if "name" in inputElement.attrs:
				options = inputElement.find_all('option')
				while inputElement['name'] not in formData.keys():
					for option in options:
						if "value" in option.attrs:
							if len(option['value']):
								if input(option.text+" (y/n): ") == "y":
									formData[inputElement['name']] = option['value']
									break
		# Prepare form
		for k in formData.keys():
			if not formData[k]:
				formData[k] = input(k+": ")

		response = self.s.post(self.base+form['action'], data=formData, allow_redirects=True)
		if response.status_code != 200:
				raise Exception("Failed to SpecifyOrderTime")

		self.viewBag.append(Soup(response.text, "html.parser"))


	def PickMenuPizzas(self):
		pass


if __name__ == "__main__":
	dominos = DominosWeb(OrderType['delivery'])
	dominos.SetOrderType()
	dominos.ProvideCustomerDetails()
	dominos.SpecifyOrderTime()
