from tqdm import tqdm
from hangman import HangmanAPI, LanguageModelHangmanAPI
              

n = 8 
weights = [5, 5, 10, 10, 10, 10, 10, 10]  

train = LanguageModelHangmanAPI(n=n, weights=weights)
test = LanguageModelHangmanAPI(n=n, weights=weights)
verbose = False
for i in tqdm(range(10)):
    train.start_game(verbose=verbose, train_test='train')
    test.start_game(verbose=verbose, train_test='test')

print('Train Win % = {0:.0%}'.format(1.0*sum(train.wins) / len(train.wins)))
print('Test Win % = {0:.0%}'.format(1.0*sum(test.wins) / len(test.wins)))
