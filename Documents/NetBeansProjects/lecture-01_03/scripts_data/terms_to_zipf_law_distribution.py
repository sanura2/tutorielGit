# Extracting pre-post retrieval features
import argparse
import os
import collections
import matplotlib.pyplot as plt


def zipf_law_distribution(terms_frequency, labelX, labelY, fig_name):
    """
        returns the zipf-law distribution of the words
    """
    sorted_terms_frequency = sorted(terms_frequency.items(), key=lambda x: x[1], reverse=True)
    frequencies = [item[1] for item in sorted_terms_frequency]

    n = len(frequencies)
    ranks = range(1, n+1)

    fig, ax = plt.subplots()
    plt.loglog(ranks, frequencies, label='alice')

    plt.title("Zipf-law distribution of the words")
    plt.ylabel(labelY)
    plt.xlabel(labelX)
    plt.xticks(rotation='270')
    #ax.set_xticklabels(deg, rotation=270, ha='right')
    #plt.show(block=False)
    plt.savefig(fig_name, format="PNG")


def get_terms_frequency(terms_inverted_documents):
    """
        returns the term with frequency
    """
    terms_frequency = {}
    for term in terms_inverted_documents:

        posting_list = terms_inverted_documents.get(term)

        sum_term_frequency = 0
        for doc_id in posting_list:
            tf = posting_list.get(doc_id)
            sum_term_frequency = sum_term_frequency + int(tf)

        terms_frequency[term] = sum_term_frequency

    return terms_frequency


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


def get_parser():
        parser = argparse.ArgumentParser(description='A program to extract features for a set of topics')
        parser.add_argument('-documents-index-path', '--documents_index_path', nargs='?', type=str, required=True,
                            help='The documents index file path')

        return parser


def parse_args():
        """
            Function used to parse the arguments provided to the script
        """

        # Parsing the args
        parser = get_parser()
        args = parser.parse_args()

        documents_index_path = args.documents_index_path
        print ("Documents index path: {}".format(documents_index_path))
        return documents_index_path


def main():

        print("Starting ... ")
        documents_index_path = parse_args()

        print ("Loading inverted index ...")
        #Indexing        
        terms_inverted_documents = get_inverted_index(documents_index_path)
        print ("Done")

        #Feature Extraction 
        print ("Extracting query features ...")
        terms_frequency = get_terms_frequency(terms_inverted_documents)
        #print (terms_frequency)
        print ("Done")

        print ("Drawing a zipf law distribution of words frequency ...")
        zipf_law_distribution(terms_frequency, "log(Rank)", "log(Freq)", "output/terms_zipf_law_distribution.png")
        print ("Done")

if __name__=="__main__":
    main()
