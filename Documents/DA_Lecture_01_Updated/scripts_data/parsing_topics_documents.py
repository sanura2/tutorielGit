import argparse
import os
import re
import sys

from bs4 import BeautifulSoup
#reload(sys)
#sys.setdefaultencoding('utf-8')

def get_extract_text_from_html( html_content ):
        """
            Extracting the clean text from a HTML document
        """
        paragraph = None
        try:
            raw = BeautifulSoup(html_content).get_text() # extracting text from html document
            lines = raw.split('\n')

            sentences = ''
            for line in lines:
                if len(line.strip())>0:
                    sentences += ' '+(line.strip())
            paragraph = sentences.strip()

        except Exception as e:
            print ("Exception in extracting the clean text from a HTML document".format(e))
        return (paragraph)


def get_topicid_title(topics_path):
        """
            Parsing and returning the topics and titles
        """
        topicid_title={}
        topicid_list=[]
        lines=[]
        with open(topics_path, 'r') as fread:
            lines = fread.readlines()

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


def get_parsed_documents(corpus_path):
        """
            Parsing a list of documents (corpus) for a set of topics
	"""
        print ("Loading all documents for all topics ...")
        topicsid_documents = {}
        with open(corpus_path, 'r', encoding="ISO-8859-1") as fread:
            lines = fread.readlines()

        total_lines = len(lines)
        print ("Total lines: {}".format(total_lines))

        iter = 0
        line = lines[iter]
        line = line.strip()
        line_parts = line.rstrip('\r\n').split(" ") #tokenization

        if len(line_parts) == 6:
            if line_parts[1] == 'Q0':
                topic_id = line_parts[0]
                document_id = line_parts[2]
                document_rank = line_parts[3]
                document_score = line_parts[4]
        iter = iter + 1

        document_content = ''
        while iter<total_lines:

            line = lines[iter]
            line = line.strip()
            line_parts = line.rstrip('\r\n').split(" ") #tokenization
            #print (line_parts)

            #check, is it a new document
            if len(line_parts) == 6:
                if line_parts[1] == 'Q0':
                    metadata = []
                    metadata.append(document_id)
                    metadata.append(document_rank)
                    metadata.append(document_score)
                    metadata.append(document_content)

                    document_metadata = topicsid_documents.get(topic_id)

                    if document_metadata is None:
                        document_metadata = []
                    document_metadata.append(metadata)
                    topicsid_documents[topic_id] = document_metadata
                    topic_id = line_parts[0]
                    document_id = line_parts[2]
                    document_rank = line_parts[3]
                    document_score = line_parts[4]
                    document_content = ''
                else:
                    document_content = document_content + ' '+ line.rstrip('\r\n')
            else:
                document_content = document_content + ' '+ line.rstrip('\r\n')
            iter = iter + 1
        #End of while

        #unfinish part of the last document
        if len(document_content)>0:
            metadata = []
            metadata.append(document_id)
            metadata.append(document_rank)
            metadata.append(document_score)
            metadata.append(document_content)

            document_metadata = topicsid_documents.get(topic_id)
            if document_metadata is None:
                document_metadata = []

            document_metadata.append(metadata)
            topicsid_documents[topic_id] = document_metadata
        return topicsid_documents


def write_topics_documents_text(topicids_list, topics_documents_text, topics_documents_path):
        """
            Writing topic_id and its related documents with metadata to a file
        """
        #open a file in write mode
        with open(topics_documents_path, 'w', encoding="utf-8") as fwriter:
            for topic_id in topicids_list:
                documents_text = topics_documents_text.get(topic_id)
                if documents_text is None:
                    continue
                for document in documents_text:
                    document_id = document[0]
                    document_rank = document[1]
                    document_score = document[2]
                    document_content = document[3]
                    #writing to file
                    fwriter.write(str(topic_id) + "\t"+ str(document_id) + "\t" + str(document_rank) +
                                  "\t"+ str(document_score) +"\t"+ str(document_content) + "\n")


def get_parser():
        """
            Initialize the parser and the parameter it can receive
        """
        parser = argparse.ArgumentParser(description='A program to parse a list of documents from a file for a set of topics')
        parser.add_argument('-corpus-path', '--corpus_path', nargs='?', type=str, required=True, help='The corpus file path')
        parser.add_argument('-topics-path', '--topics_path', nargs='?', type=str, required=True, help='The topics file path')
        parser.add_argument('-topics-documents-path', '--topics_documents_path', nargs='?', type=str,
                            required=True, help='The topic to documents output file path')
        return parser

def parse_args():
        """
            Function used to parse the arguments provided to the script
        """
        global corpus_path
        global topics_path
        global topics_documents_path

        # Parsing the args
        parser = get_parser()
        args = parser.parse_args()

        # Retrieving the args
        corpus_path = args.corpus_path
        print ("Corpus path: {}".format(corpus_path))

        topics_path = args.topics_path
        print ("Topics path: {}".format(topics_path))

        topics_documents_path = args.topics_documents_path
        print ("Topics documents path: {}".format(topics_documents_path))


corpus_path = None
topics_path = None
topics_documents_path = None
def main():
        print("Parsing arguments/input parameters ... ")
        parse_args()

        print ("Loading topics ...")
        topicsid_list, topicsid_title = get_topicid_title(topics_path)
        print ("Done")

        print ("Parsing documents ...")
        topicsid_documents_html = get_parsed_documents(corpus_path)
        print ("Done")

        print ("Extracting text from the html documents ...")
        topicsid_documents_text = {} #dictionary
        for topic_id in topicsid_list:
            topic_title = topicsid_title.get(topic_id)
            print ("Processing topic {} : {}".format(topic_id, topic_title))

            documents_list = topicsid_documents_html.get(topic_id)
            if documents_list is None:
                print ("No document parsed for topic {}".format(topic_id))
                continue
            print ("Total document for topic {} is {}".format(topic_id, len(documents_list)))
            document_text=[]
            for document in documents_list:
                html_content = document[3] #html content
                text_content = get_extract_text_from_html(html_content) #text from html document
                document_text.append([document[0], document[1], document[2], text_content])
            topicsid_documents_text[topic_id] = document_text
        print ("Done")

        print ("Total topics: {}".format(len(topicsid_documents_text)))

        print ("Writing topic and its related parsed document text ...")
        write_topics_documents_text(topicsid_list, topicsid_documents_text, topics_documents_path)
        print ("Done")

if __name__=="__main__": #The starting point of this program
    main()
