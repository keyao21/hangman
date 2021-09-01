import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from functools import partial 
from hangman import HangmanAPI, LanguageModelHangmanAPI


class HangmanUI(QMainWindow): 
    """
    Main class definition for Hangman game. 
    """
    def __init__(self):
        super().__init__()
        self.wordlength = 10
        self.number_of_tries_remaining = 6
        self.setFixedSize(800, 300)
        self.generalLayout = QVBoxLayout()
        self._centralWidget = QWidget(self)
        self.setCentralWidget(self._centralWidget)
        self._centralWidget.setLayout(self.generalLayout)

        print('initializing NLP AI...')
        _n = 8 
        _weights = [1, 1, 10, 10, 10, 10, 10, 10] 
        self.AI = LanguageModelHangmanAPI(n=_n, weights=_weights)
        # self.AI = HangmanAPI()
        print('Done.')
        
        print('Starting game...')
        self.startGame() 


    def startGame(self): 
        """
        Kick off parameter inputs, variable spaces, and UI. 
        """
        print("set up params")
        self.startParams()
        self.initParams() 
        self.initUI()


    def startParams(self): 
        """
        Start two back to back blocking dialogs to get the word lengths and number of tries. 
        """
        ParameterInputPopUp(self, "How many letters is your word?", "wordlength")
        ParameterInputPopUp(self, "How many tries are you giving the AI?", "number_of_tries_remaining")


    def initParams(self): 
        # initialize variables
        self.guessed_letters = []
        self.curr_word = ['_' for _ in range(self.wordlength)]
        self._previous_curr_word = ['_' for _ in range(self.wordlength)]
        self.current_guess_letter = None
        self.number_of_tries_remaining = self.number_of_tries_remaining_cache


    def initLabelValues(self): 
        """
        Set labels on main UI.
        """
        self.guess_label.setText("Remaining guesses : {}.".format(self.number_of_tries_remaining))
        self.word_label.setText(("  ").join(self.curr_word))
        self.current_guess_label.setText("Current guess: {}.".format(self.current_guess_letter))
        self.past_guesses_label.setText("Past guesses: {}.".format(', '.join(self.guessed_letters)))

        for i,char in enumerate(self.curr_word): 
            self.letter_placeholders[i].setText(" ")

        self.guess_next_letter()


    def initUI(self):
        """
        Set up all the buttons and stuff in the main UI.
        """
        self._start_left_idx = 30

        # set up status displays
        self.guess_label = QLabel("Remaining guesses : {}.".format(self.number_of_tries_remaining), self)
        self.guess_label.resize(400, 30)
        self.guess_label.font().setPointSize(20)
        self.guess_label.move(self._start_left_idx,5)

        self.word_label = QLabel("Current word: {}.".format(("  ").join(self.curr_word)), self)
        self.word_label.resize(400, 30)
        self.word_label.font().setPointSize(20)
        self.word_label.move(self._start_left_idx,20)

        self.current_guess_label = QLabel("Current guess: {}.".format(self.current_guess_letter), self)
        self.current_guess_label.resize(400, 30)
        self.current_guess_label.font().setPointSize(20)
        self.current_guess_label.move(self._start_left_idx,35)

        self.past_guesses_label = QLabel("Past guesses: {}.".format(', '.join(self.guessed_letters)), self)
        self.past_guesses_label.resize(400, 30)
        self.past_guesses_label.font().setPointSize(20)
        self.past_guesses_label.move(self._start_left_idx,50)

        self.guess_next_letter()

        self._start_body_idx = 90
        self.letter_placeholders = [None for _ in range(self.wordlength)]
        self.letter_buttons = [None for _ in range(self.wordlength)]
        for i,char in enumerate(self.curr_word): 
            self.letter_placeholders[i] = QLineEdit(self)
            self.letter_placeholders[i].setAlignment(Qt.AlignCenter)
            self.letter_placeholders[i].setReadOnly(True)
            self.letter_placeholders[i].resize(20, 30)
            self.letter_placeholders[i].move(self._start_left_idx+i*20, self._start_body_idx) 

            self.letter_buttons[i] = QPushButton("✔", self)
            self.letter_buttons[i].resize(20, 20)
            self.letter_buttons[i].move(self._start_left_idx+i*20, self._start_body_idx+30)   
            self.letter_buttons[i].clicked.connect(partial(self.fill_letter, i))

        self.btn = QPushButton('Guess a Letter.', self)
        self.btn.setFont(QFont('SansSerif', 10))
        self.btn.setToolTip('Guess next letter.')
        self.btn.clicked.connect(self.guess_next_letter)
        self.btn.resize(102, 43)
        self.btn.move(self._start_left_idx, self._start_body_idx+80)

        QToolTip.setFont(QFont('SansSerif', 10))
        self.setGeometry(1390, 30, 200, 270)
        self.setFixedSize(self.size())
        self.setWindowTitle('Hangman')
        self.show()


    def fill_letter(self, i): 
        self.letter_placeholders[i].setText(self.current_guess_letter)
        self.curr_word[i] = self.current_guess_letter
        self.word_label.setText(("  ").join(self.curr_word))

        if "_" not in self.curr_word: 
            self.popup = ClosingPopUp(self, f"Uh oh! Your word {''.join(self.curr_word).upper()} was guessed!")
            self.popup.setGeometry(QRect(100, 100, 400, 200))
            self.popup.show()

        QApplication.processEvents()


    def _set_previous_word(self): 
        """
        Helper function to set the previous word
        """
        self._previous_curr_word = [] 
        for w in self.curr_word: 
            self._previous_curr_word.append(w) 


    def guess_next_letter(self): 
        """
        Link to the imported Hangman API to make guesses on the next letter in the word. 
        """
        self.past_guesses_label.setText("Past guesses: {}.".format(', '.join(self.guessed_letters)))
        if self._previous_curr_word == self.curr_word:
            self.number_of_tries_remaining -= 1
            self.guess_label.setText("Remaining guesses : {}.".format(self.number_of_tries_remaining))
            if self.number_of_tries_remaining == 0: 
                self.popup = ClosingPopUp(self, "Nice! We don't know your word!")
                self.popup.setGeometry(QRect(100, 100, 400, 200))
                self.popup.show()

        _spaced_curr_word = ' '.join(s for s in self.curr_word)
        self.current_guess_letter = self.AI.guess(_spaced_curr_word)
        QApplication.processEvents()
        self.current_guess_label.setText("Current guess: "+self.current_guess_letter+" .")
        self.guessed_letters.append(self.current_guess_letter)
        self.AI.guessed_letters.append(self.current_guess_letter)
        self._set_previous_word()


class ParameterInputPopUp(QDialog): 
    """
    Class definition for initial parameter settings. 
    """
    def __init__(self, parent, msg, attr_name): 
        super().__init__()
        self.parent = parent 
        self.msg = msg
        self.attr_name = attr_name
        self.initUI()

    def setMainGuiWordLength(self): 
        setattr(self.parent, self.attr_name, int(self.letter_entry.text()))
        setattr(self.parent, self.attr_name+"_cache", int(self.letter_entry.text()))
        
        self.close()

    def initUI(self): 
        self.setWindowTitle('Set Parameters for Hangman')
        self.letter_question = QLabel(self.msg, self)
        self.letter_question.resize(200, 30)
        self.letter_question.font().setPointSize(14)
        self.letter_question.move(50,20)

        regex = QRegExp("[0-9]+")
        validator = QRegExpValidator(regex)
        self.letter_entry = QLineEdit(self)
        self.letter_entry.setValidator(validator)
        self.letter_entry.resize(30, 30)
        self.letter_entry.font().setPointSize(14)
        self.letter_entry.move(260,20)
        self.letter_entry.returnPressed.connect(self.setMainGuiWordLength)
        self.exec()


class ClosingPopUp(QWidget): 
    """
    Class definition for closing dialog that asks you to replay. 
    """
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
        self.setWindowTitle('Hangman')
        self.word_label = QLabel(self.msg, self)
        self.word_label.resize(700, 30)
        font1 = self.word_label.font()
        font1.setPointSize(14)
        self.word_label.move(50,20)
        self.replay_btn = QPushButton('Play Again', self)
        self.replay_btn.setFont(QFont('SansSerif', 13))
        self.replay_btn.setToolTip('Click to play another game of Hangman')
        self.replay_btn.clicked.connect(self.replay)
        self.replay_btn.resize(100, 40)
        self.replay_btn.move(50, 50)
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
    view = HangmanUI()
    view.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()