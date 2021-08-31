import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from functools import partial 
from hangman import HangmanAPI


class HangmanUI(QMainWindow): 
    def __init__(self, wordlength):
        super().__init__()
        self.wordlength = wordlength
        self.setFixedSize(600, 300)
        self.generalLayout = QVBoxLayout()
        self._centralWidget = QWidget(self)
        self.setCentralWidget(self._centralWidget)
        self._centralWidget.setLayout(self.generalLayout)

        print('initializing API...')
        self.AI = HangmanAPI()
        print('done.')
        
        print('Starting game...')
        self.initParams() 
        self.initUI()


    def initParams(self): 
        # initialize variables
        self._previous_curr_word = None
        self.guessed_letters = []
        self.curr_word = ['_' for _ in range(self.wordlength)]
        self.current_guess_letter = None
        self.number_of_tries_remaining = 6
        

    def initLabelValues(self): 

        self.guess_label.setText("Remaining guesses : {}.".format(self.number_of_tries_remaining))
        self.word_label.setText(("  ").join(self.curr_word))
        self.current_guess_label.setText("Current guess: {}.".format(self.current_guess_letter))
        self.past_guesses_label.setText("Past guesses: {}.".format(', '.join(self.guessed_letters)))

        for i,char in enumerate(self.curr_word): 
            self.letter_placeholders[i].setText(" ")

        self.guess_next_letter()


    def initUI(self):

        # set up status displays
        self.guess_label = QLabel("Remaining guesses : {}.".format(self.number_of_tries_remaining), self)
        self.guess_label.resize(400, 30)
        self.guess_label.font().setPointSize(20)
        self.guess_label.move(50,5)

        self.word_label = QLabel("Current word: {}.".format(("  ").join(self.curr_word)), self)
        self.word_label.resize(400, 30)
        self.word_label.font().setPointSize(20)
        self.word_label.move(50,20)

        self.current_guess_label = QLabel("Current guess: {}.".format(self.current_guess_letter), self)
        self.current_guess_label.resize(400, 30)
        self.current_guess_label.font().setPointSize(20)
        self.current_guess_label.move(50,35)

        self.past_guesses_label = QLabel("Past guesses: {}.".format(', '.join(self.guessed_letters)), self)
        self.past_guesses_label.resize(400, 30)
        self.past_guesses_label.font().setPointSize(20)
        self.past_guesses_label.move(50,50)

        self.guess_next_letter()

        self._start_body_idx = 80
        self.letter_placeholders = [None for _ in range(self.wordlength)]
        self.letter_buttons = [None for _ in range(self.wordlength)]
        for i,char in enumerate(self.curr_word): 
            self.letter_placeholders[i] = QLineEdit(self)
            self.letter_placeholders[i].setAlignment(Qt.AlignCenter)
            self.letter_placeholders[i].setReadOnly(True)
            self.letter_placeholders[i].resize(30, 30)
            self.letter_placeholders[i].move(50+i*50, self._start_body_idx) 

            self.letter_buttons[i] = QPushButton("✔", self)
            self.letter_buttons[i].resize(30, 30)
            self.letter_buttons[i].move(50+i*50, self._start_body_idx+40)   
            self.letter_buttons[i].clicked.connect(partial(self.fill_letter, i))


        self.btn = QPushButton('Guess a Letter.', self)
        self.btn.setFont(QFont('SansSerif', 10))
        self.btn.setToolTip('Guess next letter.')
        self.btn.clicked.connect(self.guess_next_letter)
        self.btn.resize(102, 43)
        self.btn.move(50, self._start_body_idx+80)

        QToolTip.setFont(QFont('SansSerif', 10))
        self.setGeometry(1390, 30, 200, 270)
        self.setFixedSize(self.size())
        self.setWindowTitle('Hangman')
        self.show()


    def fill_letter(self, i): 
        self.letter_placeholders[i].setText(self.current_guess_letter)
        self.curr_word[i] = self.current_guess_letter
        # TODO: get rid
        self.word_label.setText(("  ").join(self.curr_word))

        if "_" not in self.curr_word: 
            print(self.curr_word)
            print("sucess)")
            self.popup = ClosingPopUp(self, "Uh oh! Your word was guessed!")
            self.popup.setGeometry(QRect(100, 100, 400, 200))
            self.popup.show()

        QApplication.processEvents()


    def guess_next_letter(self): 
        
        # TODO GET RID OF THIS
        self.past_guesses_label.setText("Past guesses: {}.".format(', '.join(self.guessed_letters)))

        if self._previous_curr_word == self.curr_word: 
            self.number_of_tries_remaining -= 1
            # TODO GET RID OF THIS
            self.guess_label.setText("Remaining guesses : {}.".format(self.number_of_tries_remaining))
            if self.number_of_tries_remaining == 0: 
                print(self.curr_word)
                print("failed")
                self.popup = ClosingPopUp(self, "Nice! We don't know your word!")
                self.popup.setGeometry(QRect(100, 100, 400, 200))
                self.popup.show()
             

        _spaced_curr_word = ' '.join(s for s in self.curr_word)
        self.current_guess_letter = self.AI.guess(_spaced_curr_word)
        QApplication.processEvents()
        # todo: get rid
        self.current_guess_label.setText("Current guess: "+self.current_guess_letter+" .")
        self.guessed_letters.append(self.current_guess_letter)
        self.AI.guessed_letters.append(self.current_guess_letter)
        self._previous_curr_word = self.curr_word 


class ClosingPopUp(QWidget): 
    def __init__(self, maingui, msg): 
        super().__init__() 
        self._maingui = maingui
        self.msg = msg
        self.generalLayout = QVBoxLayout()
        self._centralWidget = QWidget(self)
        self._centralWidget.setLayout(self.generalLayout)
        self._replay = False
        self.initUI() 

    def initUI(self): 
        self.word_label = QLabel(self.msg, self)
        self.word_label.resize(400, 30)
        font1 = self.word_label.font()
        font1.setPointSize(14)
        self.word_label.move(50,20)

        self.replay_btn = QPushButton('Play Again', self)
        self.replay_btn.setFont(QFont('SansSerif', 15))
        self.replay_btn.setToolTip('Click to play another game of Hangman')
        self.replay_btn.clicked.connect(self.replay)
        self.replay_btn.resize(400, 30)
        self.replay_btn.move(50, 25)
        self.show()

    def replay(self): 
        self._maingui.initParams()
        self._maingui.initLabelValues()
        self._replay = True
        self.close() 

    def closeEvent(self, evnt): 
        # close main gui when closing pop up. 
        if not self._replay: 
            self._maingui.close() 
        super().closeEvent(evnt) 


def main():
   app = QApplication(sys.argv)
   view = HangmanUI(5)
   view.show()
   sys.exit(app.exec_())


if __name__ == '__main__':
   main()