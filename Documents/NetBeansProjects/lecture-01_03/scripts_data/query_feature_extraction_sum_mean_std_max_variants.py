# Extracting pre-post retrieval features
import argparse
import os
import nltk
import re
import nltk.data
import sys
import string
import math

from statistics import mean, stdev
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer

def sentence_to_wordlist( sentence, remove_stopwords=False ):
    """
        Tokenizing setences to words 0r terms
    """
    sentence_text = sentence
    #1. Remove non-letters
    sentence_text = re.sub("[^a-zA-Z0-9]", " ", sentence_text)

    #2. Convert words to lower case and split them
    sentence_text = sentence_text.strip()

    words = sentence_text.split( )
    #words = [word.decode("utf-8") for word in nltk.word_tokenize(sentence_text.lower()) if word not in string.punctuation]

    #3. Remove stop words (false by default)        
    if remove_stopwords:
        stops = set(stopwords.words("english"))
        words = [w for w in words if not w in stops]
    #
    #4. Return a list of words
    return (words)


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


def extract_query_features(topicsid_list, topicsid_title, documents_metadata, terms_inverted_documents):
    """
        Extract features for query using the inverted index
    """

    topics_features = {}
    N = len(documents_metadata) #total document

    for topic_id in topicsid_list:
        print ("Extracting features {}:{}".format(topic_id, topicsid_title.get(topic_id)))

        topic_title = topicsid_title.get(topic_id)
        topic_title = topic_title.lower()
        topic_title_parts = sentence_to_wordlist(topic_title, True)

        sum_df = 0.0
        sum_idf = 0.0
        sum_tf = 0.0
        sum_tfidf = 0.0

        mean_df = 0.0
        mean_idf = 0.0
        mean_tf = 0.0
        mean_tfidf = 0.0

        max_df = 0.0
        max_idf = 0.0
        max_tf = 0.0
        max_tfidf = 0.0

        std_df = 0.0
        std_idf = 0.0
        std_tf = 0.0
        std_tfidf = 0.0

        #mean, std, max of these features (to be done)
        features = []

        df_scores = []
        idf_scores = []
        tf_scores = []
        tfidf_scores = []

        query_length = len(topic_title_parts)
        for term in topic_title_parts:

            posting_list = terms_inverted_documents.get(term)
            if posting_list is None:
                continue

            df = len(posting_list)
            idf = math.log((N*1.0)/df)

            df_scores.append(df)
            idf_scores.append(idf)

            for doc_id in posting_list:
                tf = posting_list.get(doc_id)
                tf_scores.append(float(tf))

                tf_idf = float(tf) * idf
                tfidf_scores.append(tf_idf)

        if len(df_scores)>0:
            #summation variants
            sum_df = sum(df_scores)
            sum_idf = sum(idf_scores)
            sum_tf = sum(tf_scores)
            sum_tfidf = sum(tfidf_scores)

            #average variants
            mean_df = mean(df_scores)
            mean_idf = mean(idf_scores)
            mean_tf = mean(tf_scores)
            mean_tfidf = mean(tfidf_scores)

            #max variants
            max_df = max(df_scores)
            max_idf = max(idf_scores)
            max_tf = max(tf_scores)
            max_tfidf = max(tfidf_scores)

        #standard deviation
        if len(df_scores)>1:
            std_df = stdev(df_scores)
            std_idf = stdev(idf_scores)

        if len(tf_scores)>1:
            std_tf = stdev(tf_scores)
            std_tfidf = stdev(tfidf_scores)

        features.append(query_length)

        features.append(sum_df)
        features.append(sum_idf)
        features.append(sum_tf)
        features.append(sum_tfidf)

        features.append(mean_df)
        features.append(mean_idf)
        features.append(mean_tf)
        features.append(mean_tfidf)

        features.append(max_df)
        features.append(max_idf)
        features.append(max_tf)
        features.append(max_tfidf)

        features.append(std_df)
        features.append(std_idf)
        features.append(std_tf)
        features.append(std_tfidf)

        topics_features[topic_id] = features

    return topics_features


def get_documents_metadata(documents_metadata_path):
        """
            Loading document meta-data
        """
        documents_metadata = {}
        with open(documents_metadata_path, 'r') as freader:
            lines = freader.readlines()
            freader.close()

        for line in lines:
            line_parts = line.split(' ')

            document_id = line_parts[0]
            document_rank = line_parts[1]
            document_score = line_parts[2]
            document_length = line_parts[3]

            metadata = [document_rank, document_score, document_length]
            documents_metadata[document_id] = metadata
        return documents_metadata


def get_inverted_index(documents_index_path):
        """
            Loading inverted index (term -> {doc1:freq1, doc2:freq2, ...} )
        """
        terms_postinglist = {}
        with open(documents_index_path, 'r') as freader:
            lines = freader.readlines()
            freader.close()

        for line in lines:
            line_parts = line.split("\t")
            term = line_parts[0]
            posting_list = line_parts[1]
            posting_parts = posting_list.split(' ')

            documentid_freq = {}
            for item in posting_parts:
                item_parts = item.split(":")
                document_id = item_parts[0]
                frequency = item_parts[1]

                documentid_freq[document_id] = frequency
            terms_postinglist[term] = documentid_freq
        return terms_postinglist


def write_topics_features(topicsid_list, topics_features, topics_features_path):
        """
            Saving topics and its features
        """
        with open(topics_features_path, 'w') as fwriter:

            fwriter.write("Topic_id" + "\t" + "QL" + "\t" + "SUM_DF" + "\t" + "SUM_IDF" + "\t" + "SUM_TF" + "\t"+ "SUM_TFIDF")
            fwriter.write("\t" + "MEAN_DF" + "\t" + "MEAN_IDF" + "\t" + "MEAN_TF" + "\t"+ "MEAN_TFIDF")
            fwriter.write("\t" + "MAX_DF" + "\t" + "MAX_IDF" + "\t" + "MAX_TF" + "\t"+ "MAX_TFIDF")
            fwriter.write("\t" + "STD_DF" + "\t" + "STD_IDF" + "\t" + "STD_TF" + "\t"+ "STD_TFIDF" + "\n")

            for topic_id in topicsid_list:
                features = topics_features.get(topic_id)
                if features is None:
                    continue

                fwriter.write(str(topic_id))
                for feature in features:
                    fwriter.write("\t"+ str(feature))
                fwriter.write("\n")
            fwriter.close()


def get_parser():
        parser = argparse.ArgumentParser(description='A program to extract features for a set of topics')
        parser.add_argument('-topics-path', '--topics_path', nargs='?', type=str, required=True, help='The topics file path')
        parser.add_argument('-documents-metadata-path', '--documents_metadata_path', nargs='?', type=str, required=True,
                            help='The documents metadata file path')
        parser.add_argument('-documents-index-path', '--documents_index_path', nargs='?', type=str, required=True,
                            help='The documents index file path')
        parser.add_argument('-topics-features-path', '--topics_features_path', nargs='?', type=str, required=True,
                            help='The topic features file path')
        return parser

topics_path=None
documents_metadata_path=None
documents_index_path=None
topics_features_path=None
def parse_args():
        """
            Function used to parse the arguments provided to the script
        """
        global topics_path
        global documents_metadata_path
        global documents_index_path
        global topics_features_path

        # Parsing the args
        parser = get_parser()
        args = parser.parse_args()

        # Retrieving the args
        topics_path = args.topics_path
        print ("Topics path: {}".format(topics_path))

        documents_metadata_path = args.documents_metadata_path
        print ("Documents metadata path: {}".format(documents_metadata_path))

        documents_index_path = args.documents_index_path
        print ("Documents index path: {}".format(documents_index_path))

        topics_features_path = args.topics_features_path
        print ("Topics features path: {}".format(topics_features_path))


def main():

        print("Starting ... ")
        parse_args()

        print ("Loading topics ...")
        topicsid_list, topicsid_title = get_topicid_title(topics_path)
        print ("Done")

        print ("Loading document meta-dada ...")
        documents_metadata = get_documents_metadata(documents_metadata_path)
        print ("Done")

        print ("Loading inverted index ...")
        #Indexing        
        terms_inverted_documents = get_inverted_index(documents_index_path)
        print ("Done")

        #Feature Extraction 
        print ("Extracting query features ...")
        topics_features = extract_query_features(topicsid_list, topicsid_title, documents_metadata, terms_inverted_documents)
        print ("Done")

        print ("Saving topics features ...")
        write_topics_features(topicsid_list, topics_features, topics_features_path)
        print ("Done")

if __name__=="__main__":
    main()
