import csv
import numpy as np
import math
from datetime import *
from itertools import chain
import pickle
from openpyxl import Workbook

def df(word,tf):
	total = 0
	for category in tf:
		if tf[category][word] > 0:
			total += 1
	return total

def tf(data):
	# flatten list into words
	data = [(word,row[1]) for row in data for word in row[0].split(' ')]
	# get all categories
	categories = np.unique(np.array([row[1] for row in data]),return_counts=True)
	# a list of all the words, used for calculating term frequency in entire collection
	words = np.unique(np.array([row[0] for row in data]),return_counts=True)
	# initialise tf dictionary
	tfDict = {category:{word:0 for word in words[0]} for category in categories[0]}
	# calculate word frequency per category, PUT IDF IN HERE		
	for row in data:
		tfDict[row[1]][row[0]] += 1

	# calculate idfs for each word?
	n = len(categories[0]) # number of categories

	idfs = {word:math.log(n/df(word,tfDict)) for word in words[0]}
	# calculate priors
	catSum =  sum(categories[1])
	catProb = {category:categories[1][i]/catSum for i,category in enumerate(categories[0])}

	wordSum = sum(words[1])
	wordProb = {word:words[1][i]/wordSum for i,word in enumerate(words[0])}

	# calculate word probability given category
	for category in tfDict:
		catTotal = sum([tfDict[category][word] for word in tfDict[category]])
		for word in tfDict[category]:
			tfDict[category][word] =  tfDict[category][word]/catTotal*idfs[word] * catProb[category]/wordProb[word]
	return tfDict

def testing(test,trained):
	correct = 0
	test = [row for row in test if len(row[1])>0 and 'Transfer' not in row[1] and 'Credit Card' not in row[1]]
	for i in test:
		categories = [category for category in trained]
		words = i[0].split(' ')
		x = np.array([[trained[category][word] if word in trained[category] else 0 for category in categories] for word in words])
		xsums = np.sum(x,axis=0)
		if i[1] == categories[np.argmax(np.sum(x,axis=0))]:
			correct += 1
	print(correct/len(test))

def retrain():
	with open('collection.csv') as f:
		train = [row for row in csv.reader(f)]
	train = [(val[0],val[2]) for i,val in enumerate(train)]
	return tf(train)

if __name__ == "__main__":
	model = retrain()
	pickle.dump(model,open('model.pickle','wb'))
	with open('test.csv') as f:
		data = [[row[6],row[9]] for row in csv.reader(f)]
	testing(data,model)
