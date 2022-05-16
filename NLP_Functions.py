import pandas as pd
import numpy as np
import math
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.tag import pos_tag
from sentence_transformers import SentenceTransformer, util
from sklearn_extra.cluster import KMedoids

def drop_extra_data(df):
    drop_labels = ['Author_Contributions_All_Time',
                   'Author_Helpful_Votes_All_Time',
                   'Review_Helpful_Votes',
                   'Legroom',
                   'In-flight_Entertainment',
                   'Value_for_money',
                   'Check-in_and_boarding',
                   'Seat_comfort',
                   'Customer_service',
                   'Cleanliness',
                   'Food_and_Beverage']
    df.drop(columns=drop_labels, inplace = True)

#Helper function to calculate Sentence Importance Scores
def RCA_CH_CR(filename, num_reviews): 
    df = pd.read_excel(filename, nrows = num_reviews, usecols = 'B:R')

    AVERAGE_STAR = df['Stars'].mean()
    MAX_RECOMMENDATIONS = df['Review_Helpful_Votes'].max()
    FIRST_MONTH = df.iloc[0]['Month']
    FIRST_YEAR = df.iloc[0]['Year']
    LAST_MONTH = df.iloc[len(df)-1]['Month']
    LAST_YEAR = df.iloc[len(df)-1]['Year']
    DM = 12 * (FIRST_YEAR - LAST_YEAR) + (FIRST_MONTH - LAST_MONTH)

    #Prevent Divide by 0 error
    #if all reviews are from the same month, set DM to 1
    if DM == 0:
        DM = 1
    #if all reviews receive no votes, set MAX_RECOMMENDATIONS to 1
    if MAX_RECOMMENDATIONS == 0:
        MAX_RECOMMENDATIONS = 1

    authorScore = {}
    CH_col = []
    CR_col = []
    RCA_col = []

    #RCA, CH, and CR score calculations

    #Data storage format {'Author': [Sum of error, Total Reviews, ARS]}
    for review in df.itertuples():

        #RCA
        author = review.Author
        if author in authorScore.keys():
            authorScore[author][0] += abs(review.Stars - AVERAGE_STAR)/5
            authorScore[author][1] += 1
        else:
            ARS = math.log((review.Author_Helpful_Votes_All_Time/review.Author_Contributions_All_Time) + 1, 2) / 2
            ARS = ARS if ARS < 1 else 1
            authorScore[author] = [abs(review.Stars - AVERAGE_STAR)/5, 1, ARS]

        #CH
        CH_col.append(review.Review_Helpful_Votes/MAX_RECOMMENDATIONS)

        #CR
        monthsAgo = FIRST_MONTH - review.Month
        yearsAgo = FIRST_YEAR - review.Year
        CR = math.exp(-((12 * yearsAgo) + monthsAgo) / DM)
        CR_col.append(CR)
        
    #Convert to format {'Author': (AC + ARS)/2}
    for author in authorScore.keys():
        authorScore[author] = ((1 - (authorScore[author][0] / authorScore[author][1])) + authorScore[author][2]) / 2


    for i in range(len(df)):
        RCA_col.append(authorScore[df.iloc[i]['Author']])

    df['CH'] = CH_col
    df['CR'] = CR_col
    df['RCA'] = RCA_col
    
    return df

#Determines the Sentence Important scores for all sentences in the data set
def SI(data_set, review_count, W1, W2, W3):
    INDICATOR_PHRASES = ['however', 'nevertheless', 'though', 'goal', 'summaries',
                         'although', 'summary', 'results', 'as a result', 'conclusion',
                         'invention', 'even though', 'intent', 'intention', 'discussion',
                         'conclusions', 'even if', 'purpose', 'in summary', 'all in all',
                         'discussions', 'objective', 'finally', 'not with standing', 'result',
                         'not withstanding']
    
    df = RCA_CH_CR(data_set, review_count)

    drop_extra_data(df)

    max_num_words = 0
    
    #Data Storage format = {'Sentence': [w1 * LOC, w2 * IP, w3 * word_count, (RCA + CH + CR) / 3]
    CSS_score_dict = {}

    for row in df.itertuples():
        author_cred = (row.RCA + row.CH + row.CR) / 3
        
        title = row.Title.lower()
        CSS_score_dict[title] = []

        #index 0 is always 1 for a title
        CSS_score_dict[title].append(W1)

        #index 1 stores weight 2 if there is an indicator phrase in the sentence
        for word in INDICATOR_PHRASES:
            if word in title:
                CSS_score_dict[title].append(W2)
                break
        if len(CSS_score_dict[title]) == 1:
            CSS_score_dict[title].append(0)

        #index 2 stores weight 3 * the length of the sentence
        title_length = len(word_tokenize(title))
        CSS_score_dict[title].append(W3 * title_length)

        #update the max length if this sentence is the longest
        if title_length > max_num_words:
            max_num_words = title_length

        #index 3 stores the (RCA+CH+CR)/3 value
        CSS_score_dict[title].append(author_cred)

        #repeat the analysis for each sentence in the review
        sentences = sent_tokenize(row.Review)
        for sentence_num in range(len(sentences)):
            sentence = sentences[sentence_num].lower()
            CSS_score_dict[sentence] = []

            #index 0 is 1 if it is the first sentence else 0
            if sentence_num == 1:
                CSS_score_dict[sentence].append(W1)
            else:
                CSS_score_dict[sentence].append(0)

            #index 1 stores weight 2 if there is an indicator phrase in the sentence
            for word in INDICATOR_PHRASES:
                if word in sentence:
                    CSS_score_dict[sentence].append(W2)
                    break
            if len(CSS_score_dict[sentence]) == 1:
                CSS_score_dict[sentence].append(0)

            #index 2 stores weight 3 * the length of the sentence
            sentence_length = len(word_tokenize(sentence))
            CSS_score_dict[sentence].append(W3 * sentence_length)

            #update the max length if this sentence is the longest
            if sentence_length > max_num_words:
                max_num_words = sentence_length

            #index 3 stores the (RCA+CH+CR)/3 value
            CSS_score_dict[sentence].append(author_cred)

    #Convert to sentence-score format
    #Format = {'Sentence' : SI}
    SI_scores = {}
    for sentence in CSS_score_dict.keys():
        scores = CSS_score_dict[sentence]
        SI_scores[sentence] = (scores[0] + scores[1] + scores[2]/max_num_words) * scores[3]

    return SI_scores

#Uses the K-Medoids algorithm to cluster the sentences by their content (Uses the SentenceTransformer model for content vectorization)
def K_MEDOIDS(data_set, review_count, p, W1=0.3, W2=0.1, W3=0.6):
    sentence_importance_scores = SI(data_set, review_count, W1, W2, W3)
    sentence_set = list(sentence_importance_scores.keys())

    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

    k_medoids_set = list()

    for sentence in sentence_set:
        vector = model.encode(sentence)
        k_medoids_set.append(vector)

    kmedoids = KMedoids(n_clusters=p, init='random', metric='cosine', max_iter=20, random_state=0).fit(k_medoids_set)

    clusters = list()

    for x in range(p):
        clusters.append(set())

    for index in range(len(kmedoids.labels_)):
        clusters[kmedoids.labels_[index]].add(sentence_set[index])

    return clusters, sentence_importance_scores

#Returns the top k important sentences from each of p clusters as determined by the K-Medoids algorithm
def Run_Analysis(data_set, num_reviews, num_clusters, sentences_per_cluster=1, W1=0.3, W2=0.1, W3=0.6, excel=False):

    (clusters, SI_scores) = K_MEDOIDS(data_set, num_reviews, num_clusters, W1=W1, W2=W2, W3=W3)

    cluster_val = []
    
    for x in range(num_clusters):
        for y in range(sentences_per_cluster):
            cluster_val.append(x)
    
    review = []
    SI_value = []

    #Determine the top k most important sentences
    for sentences in clusters:
        topK_sentences = []
        topK_values = []
        for sentence in sentences:
            if len(topK_sentences) == 0:
                topK_sentences.append(sentence)
                topK_values.append(SI_scores[sentence])
            elif len(topK_sentences) < sentences_per_cluster:
                index = 0
                while SI_scores[sentence] > topK_values[index]:
                    index += 1
                    if index == len(topK_values):
                        break
                topK_sentences.insert(index, sentence)
                topK_values.insert(index, SI_scores[sentence])
            else:
                index = 0
                while SI_scores[sentence] > topK_values[index]:
                    index += 1
                    if index == len(topK_values):
                        break
                if index != 0:
                    topK_sentences.insert(index, sentence)
                    topK_values.insert(index, SI_scores[sentence])
                    topK_sentences.pop(0)
                    topK_values.pop(0)
                    
        review += topK_sentences
        SI_value += topK_values


    data = {'cluster': cluster_val,
            'sentence': review,
            'importance': SI_value
            }

    df = pd.DataFrame(data)

    if excel:
        df.to_excel('K-Medoids_Analysis.xlsx')

    print(df)

    return df
            

if __name__ == "__main__":
    Run_Analysis('Data_Sets/Southwest_2-15.xlsx', 20, 5, sentences_per_cluster=2)

