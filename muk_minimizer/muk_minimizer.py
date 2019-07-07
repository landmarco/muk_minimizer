#!/usr/bin/env python
import sys

import jsonlines
from gensim.summarization.summarizer import summarize
import re

#TODO: implement other version of non-gensim summarizer
def simple_text_summarizer(raw_docx):
    raw_text = raw_docx
    docx = nlp(raw_text)
    stopwords = list(STOP_WORDS)
    # Build Word Frequency
    word_frequencies = {}  
    #TODO: normalize data further with better handling of symbols and dropping infrequent words
    words_nostops = [word.text for word in docx if word.text not in stopwords]
    for word in words_nostops:
        if word not in word_frequencies.keys():
            word_frequencies[word] = 1
        else:
            word_frequencies[word] += 1


    maximum_frequncy = max(word_frequencies.values())

    for word in word_frequencies.keys():  
        word_frequencies[word] = (word_frequencies[word]/maximum_frequncy)
    # Sentence Tokens
    sentence_list = [ sentence for sentence in docx.sents ]

    # Calculate Sentence Score and Ranking
    sentence_scores = {}  
    for sent in sentence_list:  
        for word in sent:
            if word.text.lower() in word_frequencies.keys():
                if len(sent.text.split(' ')) < 30:
                    if sent not in sentence_scores.keys():
                        sentence_scores[sent] = word_frequencies[word.text.lower()]
                    else:
                        sentence_scores[sent] += word_frequencies[word.text.lower()]

    # Find N Largest
    summary_sentences = nlargest(7, sentence_scores, key=sentence_scores.get)
    final_sentences = [ w.text for w in summary_sentences ]
    summary = ' '.join(final_sentences)
    print("Original Document\n")
    print(raw_docx)
    print("Total Length:",len(raw_docx))
    print('\n\nSummarized Document\n')
    print(summary)
    print("Total Length:",len(summary))

#TODO: visualization of what NLP is determining as contentful

def jsonl_importer(filename):
    with jsonlines.open(filename) as reader:
        case_list = [obj for obj in reader]
    return case_list

def choose_case(case_list, selection):
    return case_list[selection]

def sentence_context(sentence, text):
    full_context = re.search("([^\n]*\n)?[^\n]*" +
              re.escape(sentence) +
              "[^\n]*(\n[^\n]+)?", text)
    return full_context.group()

def containing_paragraph(sentence, text):
    paragraph = re.search("([^\n]*)?" +
                            re.escape(sentence) +
                            "([^\n]*\n)?", text)
    return paragraph.group()

def get_case_opinions(case_json):
    #TODO: extend to make clear which is majority and which is minority opinion
    ops = [op for op in case_json['casebody']['data']['opinions']]
    return ops

def collect_header(case_json):
    name = case_json['name']
    court = case_json['court']['name']
    date = case_json['decision_date']
    return '\n'.join([name, court,date])
    #return name, judges, court, date

    #judges = '\n'.join(case_json['casebody']['data']['judges'])
    
def collect_opinion_summaries(ops, ratio=0.2):
    ops_text = ''
    for op in ops:
        ops_text = ops_text + op['type'] + ' opinion\nauthor: ' + \
        op['author'] + '\nSUMMARY AT A {:.2f} COMPACTION RATIO:\n'.format(ratio) + \
        summarize(op['text']) + \
        '\n\n\n\n\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n\n\n\nORIGINAL TEXT:\n' + \
        op['text'] + '\n'
    return ops_text
    
def complete_summary(case_json, ratio=0.2):
    header = collect_header(case_json)
    ops = get_case_opinions(case_json)
    summaries = collect_opinion_summaries(ops, ratio)
    complete_text = '\n'.join([header,summaries])
    return complete_text

def arbitrary_text_summarizer(text, ratio=0.2):
    summarized_text = summarize(text)
    formatted_summary = "SUMMARY AT A {:.2f} COMPACTION RATIO:\n".format(ratio) + \
        summarized_text + \
        '\n\n\n\n\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n\n\n\nORIGINAL TEXT:\n' + \
        text
    return formatted_summary
    


 main():
    """Minimize a law text using extractive summary."""

    # Save arguments and options
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    opts = [o for o in sys.argv[1:] if o.startswith("-")]

    if args:
        for arg in args:
            filename = arg
            case_list = jsonl_importer(filename)
            case_json = choose_case(case_list, 2) #TODO incorporate which case you are choosing
            summary = complete_summary(case_json, ratio=2) #TODO selecting the ratio
            return summary


if __name__ == "__main__":
    main()
