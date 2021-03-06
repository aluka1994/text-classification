from nltk import word_tokenize
from nltk.corpus import reuters 
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.stem.porter import PorterStemmer
from collections import defaultdict
import re
from nltk.corpus import stopwords
import csv

cachedStopWords = stopwords.words("english")

def tokenize(text):
	min_length = 3
	words = map(lambda word: word.lower(), word_tokenize(text));
	words = [word for word in words if word not in cachedStopWords]
	tokens =(list(map(lambda token: PorterStemmer().stem(token), words)));
	p = re.compile('[a-zA-Z]+');
	filtered_tokens = list(filter(lambda token: p.match(token) and len(token)>=min_length, tokens));
	return filtered_tokens

# Return the representer, without transforming
def tf_idf(docs):	
	tfidf = TfidfVectorizer(tokenizer=tokenize, min_df=3, max_df=0.90, max_features=1000, use_idf=True, sublinear_tf=True);
	tfidf.fit(docs);
	return tfidf;

def feature_values(doc, representer):
	doc_representation = representer.transform([doc])
	features = representer.get_feature_names()
	return [(features[index], doc_representation[0, index]) for index in doc_representation.nonzero()[1]]

def collection_stats():
	# List of documents
	documents = reuters.fileids()
	print(str(len(documents)) + " documents");
	
	train_docs = list(filter(lambda doc: doc.startswith("train"), documents));
	print(str(len(train_docs)) + " total train documents");
	
	test_docs = list(filter(lambda doc: doc.startswith("test"), documents));	
	print(str(len(test_docs)) + " total test documents");

	# List of categories 
	categories = reuters.categories();
	print(str(len(categories)) + " categories");

	# Documents in a category
	category_docs = reuters.fileids("acq");

	# Words for a document
	document_id = category_docs[0]
	document_words = reuters.words(category_docs[0]);
	print(document_words);	

	# Raw document
	print(reuters.raw(document_id));



inverted_index_train = {}
inverted_index_test = {}
inverted_index_train_pruned = {}
inverted_index_test_pruned = {}
frequent_item_list = []

def build_index_train(doc_data,doc_id):
	for i in doc_data:
		doc_list  = []
		if i in inverted_index_train:
			doc_list = inverted_index_train[i]
			if doc_id in doc_list:
				continue
			else:
				doc_list.append(doc_id)				
		else:
			doc_list.append(doc_id)
		inverted_index_train[i] = doc_list	

def build_index_test(doc_data,doc_id):
	for i in doc_data:
		doc_list  = []
		if i in inverted_index_test:
			doc_list = inverted_index_test[i]
			if doc_id in doc_list:
				continue
			else:
				doc_list.append(doc_id)				
		else:
			doc_list.append(doc_id)
		inverted_index_test[i] = doc_list	

def generate_train_csv():

	with open("sentences_train.csv","wb") as f:
		writer = csv.writer(f,quoting=csv.QUOTE_ALL)	
		for doc_id in reuters.fileids():
			if doc_id.startswith("train"):
				raw_data = reuters.raw(doc_id).split('.')
				for sentence in raw_data:
					#sentence_list=[]
					if  len(tokenize(sentence)) >= 3:
						writer.writerow(tokenize(sentence))


def extract_csv():

	with open('frequent_train_set.csv','rb') as f:
		reader = csv.reader(f)
		for word in list(reader):
			frequent_item_list.append(word)		


def main():
	train_docs = [] # contains train document numbers
	test_docs = []  # contains test document numbers
	train_category_docs = {}  # contains category corresponding train documents
	test_category_docs = {}   # contains category corresponding test documents
	train_data = {}  # contains train document numbers corresponding data
	test_data = {}	 # contains test document numbers corresponding data
	

	categories = reuters.categories() # Total categories list

	#print categories

	#print "Category Name" + " <------------------> " +  "No of Train documents in each Category"
	with open("category_train_docs.csv","wb") as f:
		writer = csv.writer(f,quoting=csv.QUOTE_ALL)
		for category_name in categories:
			category_docs = reuters.fileids(category_name)
			#print category_name + " <------------------> " + str(len(category_docs))
			train_list = []
			test_list = []
			for category_id in category_docs:	
				if category_id.startswith("train"):
					train_list.append(category_id.split('/')[1])
					
				else:
					test_list.append(category_id.split('/')[1])
			writer.writerow([category_name] + train_list)		
			#test_category_docs[category_name] = test_list
			#train_category_docs[category_name] = train_list

	exit()	

	for doc_id in reuters.fileids():
		if doc_id.startswith("train"):		
			train_docs.append(doc_id)
			train_data[doc_id] = tokenize(reuters.raw(doc_id))
			doc_number = doc_id.split('/')[1]
			build_index_train(tokenize(reuters.raw(doc_id)),doc_number)
			#train_docs.append(reuters.raw(doc_id))
		else:
			test_docs.append(doc_id)
			test_data[doc_id] = tokenize(reuters.raw(doc_id))
			doc_number = doc_id.split('/')[1]
			build_index_test(tokenize(reuters.raw(doc_id)),doc_number)

	#print train_data	
	

	with open("inverted_train_index.csv","wb") as f:
		writer = csv.writer(f,quoting=csv.QUOTE_ALL)
		for words in inverted_index_train:
			if len(inverted_index_train[words]) >= 3:
				inverted_index_train_pruned[words] = (inverted_index_train[words])
				writer.writerow([words] + inverted_index_train_pruned[words])


	for words in inverted_index_test:
		if len(inverted_index_test[words]) >= 3:
			inverted_index_test_pruned[words] = inverted_index_test[words] 

	#print len(inverted_index_train_pruned)
	#print len(inverted_index_test_pruned)
	#print len(train_docs)
	#print len(test_docs)


#extract_csv()
#generate_train_csv()
#main()
#print frequent_item_list

if __name__ == '__main__':
	
	main()
		