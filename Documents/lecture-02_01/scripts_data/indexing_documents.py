import argparse
import os
import nltk
import re
import nltk.data
import sys
import string

from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer


def sentence_to_wordlist( sentence, remove_stopwords=False ):
    """
        Tokenize a sentence into terms
    """
    #Function to convert a sentence to a sequence of words
    sentence_text = sentence

    #2. Remove non-letters
    sentence_text = re.sub("[^a-zA-Z0-9]", " ", sentence_text)

    #3. Convert words to lower case and split them
    sentence_text = sentence_text.strip()
    print (sentence_text)
    words = sentence_text.split()
    #words = [word.decode("utf-8") for word in nltk.word_tokenize(sentence_text.lower()) if word not in string.punctuation]

    #5. Remove stop words (false by default)        
    if remove_stopwords:
        stops = set(stopwords.words("english"))
        words = [w for w in words if not w in stops]
    return (words)


def indexing(document_id, document_content, terms_posting_list):
        """
            Indexing a document and update the terms' posting list
        """
        document_content = document_content.lower() #lower case the text
        document_terms = sentence_to_wordlist(document_content, True) #tokenize the text to terms

        for term in document_terms:
            posting_list = terms_posting_list.get(term)
            if posting_list is None:
                posting_list = {}

            #frequency
            term_frequency = posting_list.get(document_id)
            if term_frequency is None:
                term_frequency = 0

            term_frequency = term_frequency + 1
            posting_list[document_id] = term_frequency
            terms_posting_list[term] = posting_list


def get_documents_inverted_index_and_metadata(topicsid_list,  topicsid_documents_list):
        """
            Indexing all documents for all topics and keep document's meta-data
        """
        documentsid_metadata = {}
        terms_posting_list = {}

        for topic_id in topicsid_list:
            print ("processing topic: {}".format(topic_id))
            documents_list = topicsid_documents_list.get(topic_id)
            if documents_list is None:
                continue

            for document in documents_list:
                print (document)

                document_id = document[0]
                document_rank = document[1]
                document_score = document[2]
                document_content = document[3]
                document_length = len(document_content.split(' '))
                metadata = [document_rank, document_score, document_length]
                documentsid_metadata[document_id] = metadata

                #indexing
                indexing( document_id, document_content, terms_posting_list)
        return terms_posting_list, documentsid_metadata


def get_topicid_title(topics_path):
        """
            Loading query-id and title
        """
        topicid_title = {}
        topicid_list = []
        lines =[]
        with open(topics_path, 'r') as fread:
            lines = fread.readlines()
            fread.close()

        total_lines = len(lines)
        iter = 0
        while iter<total_lines:

            line = lines[iter]
            line = line.rstrip('\n\r')
            line_parts = line.split(':')

            topic_id = line_parts[0]
            topic_title = line_parts[1]

            topicid_list.append(topic_id)
            topicid_title[topic_id] = topic_title

            iter = iter + 1
        return topicid_list, topicid_title

def get_topicsid_documents_list(topics_documents_path):
        """
            Loading the documents for a set of topics
        """
        topicsid_documents_list = {}
        print ("Loading all documents for all topics ... ")
        with open(topics_documents_path, 'r') as fread:
            lines = fread.readlines()
            fread.close()

        total_lines = len(lines)
        print ("Total lines: {}".format(total_lines))
        print ("Reading each line")

        for line in lines:
            line_parts = line.split('\t')
            topic_id = line_parts[0]
            document_id = line_parts[1]
            document_rank = line_parts[2]
            document_score = line_parts[3]
            document_content = line_parts[4]

            document = [document_id, document_rank, document_score, document_content]
            documents_list = topicsid_documents_list.get(topic_id)

            if documents_list is None:
                documents_list = []
            documents_list.append(document)
            topicsid_documents_list[topic_id] = documents_list
        print ("Done")
        return topicsid_documents_list


def write_documents_metadata(documents_metadata, documents_metadata_path):
        """
            Saving document meta-data
        """
        with open(documents_metadata_path, 'w') as fwriter:
            for document_id in documents_metadata:
                metadata = documents_metadata.get(document_id)
                line = document_id

                for item in metadata:
                    line = line + ' '+str(item)
                line = line.strip()
                fwriter.write(line + "\n")
            fwriter.close()


def write_inverted_index(terms_inverteddocuments, documents_index_path):
        """
            Saving inverted index (term -> {doc1:freq1, doc2:freq2, ...})
        """
        with open(documents_index_path, 'w') as fwriter:
            for term in terms_inverteddocuments:
                posting_list = terms_inverteddocuments.get(term)
                line = ''
                for document_id in posting_list:
                    term_frequency = posting_list.get(document_id)
                    line = line + ' '+str(document_id)+':'+str(term_frequency)

                line = line.strip()
                fwriter.write(str(term) + "\t"+ line + "\n")
            fwriter.close()


def get_parser():
    parser = argparse.ArgumentParser(description='A program to index a list of documents for a set of topics')
    parser.add_argument('-topics-path', '--topics_path', nargs='?', type=str, required=True, help='The topics file path')
    parser.add_argument('-topics-documents-path', '--topics_documents_path', nargs='?', type=str, required=True, 
                        help='The topic to documents file path')
    parser.add_argument('-documents-metadata-path', '--documents_metadata_path', nargs='?', type=str, 
                        required=True, help='The documents metadata file path')
    parser.add_argument('-documents-index-path', '--documents_index_path', nargs='?', type=str, required=True, 
                        help='The documents index file path')
    return parser

topics_path = None
topics_documents_path = None
documents_metadata_path = None
documents_index_path = None

def parse_args():
        """
            function used to parse the arguments provided to the script
        """
        global topics_path
        global topics_documents_path
        global documents_metadata_path
        global documents_index_path

        # Parsing the args
        parser = get_parser()
        args = parser.parse_args()

        # Retrieving the args
        topics_path = args.topics_path
        print ("Topics path: {}".format(topics_path))

        topics_documents_path = args.topics_documents_path
        print ("Topics documents path: {}".format(topics_documents_path))

        documents_metadata_path = args.documents_metadata_path
        print ("Documents metadata path: {}".format(documents_metadata_path))

        documents_index_path = args.documents_index_path
        print ("Documents index path: {}".format(documents_index_path))


def main():

        print("Starting ... ")
        parse_args()

        print ("Loading topics ...")
        topicsid_list, topicsid_title = get_topicid_title(topics_path)
        print ("Done")

        print ("Loading documents for all the topics ...")
        topicsid_documents_list = get_topicsid_documents_list(topics_documents_path)
        print ("Done")

        print ("Inverted indexing documents ...")
        terms_inverteddocuments, documents_metadata = get_documents_inverted_index_and_metadata(topicsid_list, 
                topicsid_documents_list)
        print ("Done")

        print ("Saving documents meta-data ...")
        write_documents_metadata(documents_metadata, documents_metadata_path)
        print ("Done")

        print ("Saving inverted index ...")
        write_inverted_index(terms_inverteddocuments, documents_index_path)
        print ("Done")


if __name__=="__main__":

    main()
