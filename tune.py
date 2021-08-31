from tqdm import tqdm
from hangman import HangmanAPI, LanguageModelHangmanAPI
                        

verbose = False
n = 8
weights_trials =  [
            [1,2, 4, 5, 8, 8, 10, 10],
            # [1,5, 5, 5,10,10, 5, 5],
            [1,1, 2, 2, 1, 1, 1, 1],
            [1,1, 1, 2, 2, 2, 2, 2],
            # [1,1, 1,10,10,10,10, 10],
            [1,1,10,10,10,10,10, 10],
            [1,1, 6, 8,10, 6, 6, 6],
            [5,5, 8,10, 8, 5, 5, 5],
            # [1,1, 1,10,10, 0, 0, 0],
            [1,1, 1,10,10,10,10, 10],
            [1,1,10,10,10,10,10, 10],
            [1,1, 6, 8,10, 6, 6, 6],
            [5,5, 8,10, 8, 5, 5, 5],
        ]
for sample_weights in weights_trials: 
	train = LanguageModelHangmanAPI(n=n, weights=sample_weights)
	test = LanguageModelHangmanAPI(n=n, weights=sample_weights)
	for i in tqdm(range(500)):
	    train.start_game(verbose=verbose, train_test='train')
	    test.start_game(verbose=verbose, train_test='test')
	print("weights:", sample_weights)
	print('Train Win % = {0:.0%}'.format(1.0*sum(train.wins) / len(train.wins)))
	print('Test Win % = {0:.0%}'.format(1.0*sum(test.wins) / len(test.wins)))
