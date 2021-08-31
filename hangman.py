import json
import requests
import random
import string
import secrets
import time
import re
import collections
import numpy as np 


class HangmanAPI(object):
    def __init__(self, n=5, weights=[1,2,3,5,8]):
        self.guessed_letters = []
        self.incorrect_guesses = []
        
        full_dictionary_location = "dictionaries/words_250000_train.txt"
        test_dictionary_location = "dictionaries/words_test.txt"
        self.full_dictionary = self.build_dictionary(full_dictionary_location)  
        self.full_dictionary_common_letter_sorted = collections.Counter("".join(self.full_dictionary)).most_common()      
        self.test_dictionary = self.build_dictionary(test_dictionary_location)
        
        self.n = n
        self.ngram_dictionaries = [None] 
        self.ngram_dictionaries += [
            self.create_ngram_dictionary(i, self.full_dictionary)
            for i in range(1, self.n+1)
        ]
        self.ngram_model_weights = weights
        assert(len(self.ngram_model_weights) == self.n)

        self.current_dictionary = []
        self.wins = []
        self.lose_words = []
        

    def get_end_points(self, n): 
        # returns list of tuples of length n
        return [(i, -n+1+i) for i in range(n)]


    def list_of_n_tups(self, n, s): 
        # returns list of n tuples of characters from string s
        l = len(s)
        return list(zip(*[s[b:l+e] for b,e in self.get_end_points(n)]))


    def create_ngram_dictionary(self, n, dictionary): 
        s = " ".join(dictionary)
        all_ngrams = []
        for tup in self.list_of_n_tups(n, s): 
            if ' ' not in tup: 
                all_ngrams.append("".join(tup))   
        ngram_dictionary = collections.Counter(all_ngrams)
        return ngram_dictionary


    def ngram_model(self, n, word, dictionary=None): 
        # trigram model
        # returns dictionary -> { letter : normalized weight }
        if dictionary: 
            ngram_dictionary = self.create_ngram_dictionary(n, dictionary)
        else: 
            ngram_dictionary = self.ngram_dictionaries[n]

        candidate_letters = collections.defaultdict(int)
        for ngram_tuple in self.list_of_n_tups(n, word):
            if ngram_tuple.count('.') == 1:
                ngram_regex = "".join(ngram_tuple)
                prog = re.compile(ngram_regex)
                for ngram, weight in ngram_dictionary.items(): 
                    match = prog.match(ngram)
                    if match: 
                        for i, c_i in enumerate(ngram_regex): 
                            if c_i == ".": 
                                candidate_letters[ngram[i]] += weight
        total_weight = sum(candidate_letters.values())
        normalized_candidate_letters = { 
            letter : weight/total_weight
            for letter, weight in candidate_letters.items()
        }
        return normalized_candidate_letters


    def guess(self, word): 
        clean_word = word[::2].replace("_",".")
        ngram_model_probs = [
            self.ngram_model(n, clean_word)
            for n in range(1,self.n+1)
        ]    
        
        scores = dict()
        max_score = 0
        suggested_letter = None
        for cord in range(ord('a'), ord('z')+1): 
            if chr(cord) in self.guessed_letters: 
                continue
            score = sum([
                self.ngram_model_weights[i]*ngram_model_probs[i].get(chr(cord), 0)
                for i in range(self.n)
            ])
            
            scores[chr(cord)] = score
            if score > max_score: 
                max_score = score
                suggested_letter = chr(cord)
        # print(scores)
        return suggested_letter

  
    def build_dictionary(self, dictionary_file_location):
        text_file = open(dictionary_file_location,"r")
        full_dictionary = text_file.read().splitlines()
        text_file.close()
        return full_dictionary

              
    def play_game(self, verbose=True): 
        '''
        Plays a game with the user, where the user decides whether the letter is correct or not.  
        '''
        # reset guessed letters to empty set and current plausible dictionary to the full dictionary
        self.guessed_letters = []
        self.tries_remaining = 6 
        
        length_of_word = int(input("\nHow long is the word?"))
        masked = ['_' for letter in range(length_of_word)]
    
        word = ' '.join(masked)
        # breakpoint()
        while self.tries_remaining > 0:
            
            if verbose:
                print("{} tries remaining".format(self.tries_remaining))
                print(word)
                print('\n')
            
            my_guess = self.guess(word)
            
            self.guessed_letters.append(my_guess)
            
            if verbose:
                print("The letter {} is guessed".format(my_guess))
                print('\n')

            yn = input("is letter {} in the word?".format(my_guess))
            if yn in {'Y', 'y', 'yes', 'YES', 'Yes'}: 
                locstr = input("where is/are the letter(s)? (Enter as comma delimited)")
                indices = [int(loc)-1 for loc in locstr.split(',')]

                # indices = []
                # indices = [i for i, x in enumerate(characters) if x == my_guess]
                
                for index in indices:
                    masked[index] = my_guess
                    
                word = ' '.join(masked)
                
                if '_' not in word:
                    if verbose:
                        print(word)
                        print('You win!')
                    self.wins.append(1)
                    break
            else: 
                if verbose:
                    print("Bad guess")
                    print('\n')
                self.tries_remaining = self.tries_remaining - 1
                
        if '_' in word:
            if verbose:
                print("You lose!")
            self.wins.append(0)
            self.lose_words.append(actual_word)




    def start_game(self, verbose=True, train_test='train'):
        '''
        Plays a single game of hangman. Specify whether or not to use a word from the training
        dictionary or the test dictionary
        '''
        
        # reset guessed letters to empty set and current plausible dictionary to the full dictionary
        self.guessed_letters = []
        self.tries_remaining = 6 


        if not actual_word:
            if train_test == 'train':
                actual_word = random.choice(self.full_dictionary)
            else:
                actual_word = random.choice(self.test_dictionary)
        
        if verbose and see_actual:
            print('The word is {}'.format(actual_word))
            
        characters = [i for i in actual_word]
        
        masked = ['_' for letter in characters]
    
        word = ' '.join(masked)
        # breakpoint()
        while self.tries_remaining > 0:
            
            if verbose:
                print("{} tries remaining".format(self.tries_remaining))
                print(word)
                print('\n')
            
            my_guess = self.guess(word)
            
            self.guessed_letters.append(my_guess)
            
            if verbose:
                print("The letter {} is guessed".format(my_guess))
                print('\n')
        
            if my_guess in characters:
                indices = [i for i, x in enumerate(characters) if x == my_guess]
                
                for index in indices:
                    masked[index] = my_guess
                    
                word = ' '.join(masked)
                
                if '_' not in word:
                    if verbose:
                        print(word)
                        print('You win!')
                    self.wins.append(1)
                    break
    
            else:
                if verbose:
                    print("Bad guess")
                    print('\n')
                self.tries_remaining = self.tries_remaining - 1
                
        if '_' in word:
            if verbose:
                print("You lose!")
            self.wins.append(0)
            self.lose_words.append(actual_word)


class LanguageModelHangmanAPI(HangmanAPI): 
    def __init__(self, n=8, weights=[1,1,1,1,1,1,1,1]): 
        
        super().__init__()
        
        ##################################################################
        # Below are class attributes, specific to n-grams language model.#
        ##################################################################
        self.n = n
        self.ngram_distributions = [None] 
        self.ngram_distributions += [
            self.create_ngram_distribution(i, self.full_dictionary)
            for i in range(1, self.n+1)
        ]
        self.letter_exist_distributions = \
            self.create_letter_existence_distributions(self.full_dictionary)
        self.ngram_model_weights = weights
        assert(len(self.ngram_model_weights) == self.n)
    

    def get_end_points(self, n): 
        # returns list of tuples of length n
        return [(i, -n+1+i) for i in range(n)]

    
    def list_of_n_tups(self, n, s): 
        # returns list of n tuples of characters from string s
        l = len(s)
        return list(zip(*[s[b:l+e] for b,e in self.get_end_points(n)]))


    def encode_word(self, word): 
        # convert string word to 26 length list
        encoded_word = np.zeros(26)
        base_ordinal = ord("a")
        for c in word: 
            cid = ord(c) - base_ordinal
            encoded_word[cid] = 1
        return encoded_word


    def create_letter_existence_distributions(self, dictionary): 
        """
        Create a probability distribution across letters according 
        to the probability of their EXISTENCE (max 1 per word) by word lengths. 
        A brief investigations into the provided dictionaries showed me that
        letter existence probabilities' ranking changes as word lengths 
        change. 

        For example, "y" exists in ~20% of 11 length words, but 40% of 
        19 length words! Nevertheless, we only really care about the top couple of
        letters, which are generally more consistent (e.g. i, e, t, a, r, s) but 
        sometimes switch rankings between them. 

        Returns python dict : {length -> character -> probability}
        """

        letter_distributions = np.zeros((50, 26)) # word length, character ordinal
        letter_counts_track = np.zeros(50) # record number of words with i number of letters.

        for word in dictionary: 
            letter_distributions[len(word)] += self.encode_word(word)
            letter_counts_track[len(word)] += 1 

        letter_distributions_dict = dict() 
        base_ordinal = ord("a")
        for length, letter_counts in enumerate(letter_distributions): 
            letter_distributions_dict[length] = dict()
            for rel_ord, count in enumerate(letter_counts):  
                prob = count / letter_counts_track[length]
                letter_distributions_dict[length][chr(base_ordinal+rel_ord)] = prob

        return letter_distributions_dict


    def create_ngram_distribution(self, n, dictionary): 
        """
        Create a n-gram model (probability distribution) 
        based on a dictionary of words and counting the n-grams. 
        """
        s = " ".join(dictionary)
        all_ngrams = []
        for tup in self.list_of_n_tups(n, s): 
            all_ngrams.append("".join(tup))   
        ngram_distribution = collections.Counter(all_ngrams)
        return ngram_distribution


    def ngram_model(self, n, word, dictionary=None): 
        """
        Returns the conditional probability distribution of letters missing in word
        in the form of a python dict -> { letter : conditional probability }
        
        Given the current word (e.g. " h.l.o. ", notice the spaces at the start and end of the word) 
        where "."s represent missing letters, all n-grams of the word are checked 
        against the prior distribution of n-grams; each n-gram holds a weight (number of times 
        n-gram has occured in corpus).
        
        For example, if n=3 and if the prior distribution only contains 
        
        {
            "on ": 200,
            "eal": 500, 
            "llo": 400,
            "hal": 400,
            "lio": 500,
        }, 
        
        the n-grams (3-grams) from the words that match words in the prior distribution
        are WHERE THERE IS ONLY ONE MISSING LETTER (i.e. ".l." matches "llo", but there are
        2 missing letters so it is not considered in the calculation): 
        
        "o. " matches "on ",
        "l.o" matches "llo", "lio",
        "h.l" matches "hal",
        
        Each pairing between the n-grams (3-grams) and words in the prior distribution 
        is recorded in a dictionary which stores the total weight per candidate letter. 
        For the example above, the dictionary, or posterior distribution 
        of letter weights, would become: 
        
        {
            "l" : 400 + 400, 
            "i" : 500, 
            "e" : 500,
            "a" : 400,
            "n" : 200,
        }
        
        In this case, "l" ends up having the highest total weight (which is then divided 
        by the total weights across every candidate letter to get the probability), so 
        our model says there's ~33% chance "l" is a letter in the word. There's ~20% "i"
        is in the word, ~20% "e" is in the word, ~17% "a" is the word, etc. 
        
        In other words, we are going from the prior probability distribution
        of n-grams to a posterior probability distribution of candidate letters. 

        Note 1: We remove " " from candidate letters because we know for a fact there 
        are no " "s in the word besides at the start and end. 
                
        Note 2: if a dictionary is provided, we create an n-gram probability distribution
        based on it. Else, we will use the original n-gram probability distribution
        that is stored in memory. 

        """
        if n == 1: 
            # return a letter distribution based on the word length, not n-grams model. 
            # remember to subtract 2 because SPACES are added to the word!!
            # also, winsorize distribution to be only greater than 3 and less than 19 
            #   bc everything else has fewer than 1000 samples per word length.
            length_winsorized = min(max(len(word)-2, 3), 19)
            return self.letter_exist_distributions[length_winsorized]

        if dictionary: 
            prior_ngram_distribution = self.create_ngram_distribution(n, dictionary)
        else: 
            prior_ngram_distribution = self.ngram_distributions[n]

        
        posterior_letter_distribution = collections.defaultdict(int)
        for ngram_tuple in self.list_of_n_tups(n, word):
            if ngram_tuple.count('.') == 1:
                ngram_regex = "".join(ngram_tuple).replace(".", "[^ ]")
                prog = re.compile(ngram_regex)
                for ngram, weight in prior_ngram_distribution.items(): 
                    match = prog.match(ngram)
                    if match: 
                        for i, c_i in enumerate(ngram_regex.replace("[^ ]",".")): 
                            if c_i == ".": 
                                posterior_letter_distribution[ngram[i]] += weight

        if " " in posterior_letter_distribution.keys(): 
            del posterior_letter_distribution[" "]
        total_weight = sum(posterior_letter_distribution.values())
        normalized_posterior_letter_distribution = { 
            letter : weight/total_weight
            for letter, weight in posterior_letter_distribution.items()
        }
        return normalized_posterior_letter_distribution
    
    
    
    def guess(self, word): 
        clean_word = word[::2].replace("_",".")
        clean_word = " " + clean_word + " "

        ngram_model_probs = [
            self.ngram_model(n, clean_word)
            for n in range(1,self.n+1)
        ]    
        
        scores = dict()
        max_score = 0
        suggested_letter = None
        for cord in range(ord('a'), ord('z')+1): 
            if chr(cord) in self.guessed_letters: 
                continue
            score = sum([
                self.ngram_model_weights[i]*ngram_model_probs[i].get(chr(cord), 0)
                for i in range(self.n)
            ])
            
            scores[chr(cord)] = score
            if score > max_score: 
                max_score = score
                suggested_letter = chr(cord)
        # print(scores)
        return suggested_letter