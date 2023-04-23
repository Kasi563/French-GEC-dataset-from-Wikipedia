"""
This is a script containing a CorruptText class capable of corrupting a string based on a probability parameter. Corrupting by either a character permutation, deletion, addition, or substitution. The probability parameter reflects the sum of the probabilites of one of these actions occuring. The probability for each action is equal to (1/number of action)*probability.

To implement a quality addition and substitution action, an internal dictionary is created by using a corpus of text. The keys are composed of every unique characters present in the corpus. The values (floats between 0 and 1) reflects the square root of the character occurrency in the corpus. The sum of the values is equal to 1. This choice makes it so that the corruption looks more "human like", instead of randomly selecting the latin alpbabet and punctuation.

The file includes a create_corrupter which creates a CorruptText instance and loads, if specified, a .pkl file containing the alpbet (the discussed dictionary) and loads it to the CorruptText instance. For creation of such an alphabet, please use the create_alphabet_probabilities function.
"""
import re
import random
import pickle
import polars as pl
from tqdm import tqdm
from .get_file_names import get_file_names


class CorruptBaseline:

    def __init__(self, corpus="Lorem Ipsum"):
        self.whitespace_char_freq_divider = 20
        if isinstance(corpus, str):
            self._set_alphabet(corpus)

    def permutate(self, iterable: list, probability=0.1):
        self._check_probability(probability)

        # Iterate over pairs of adjacent characters in the list
        for i in range(len(iterable) - 1):
            if random.random() < probability:
                # Swap the characters if the random number is less than the probability
                iterable[i], iterable[i+1] = iterable[i+1], iterable[i]
        
        return iterable


    def delete(self, iterable: list, probability=0.1):
        self._check_probability(probability)
        result = []

        # Iterate over pairs of adjacent characters in the list
        for element in iterable:
            if not random.random() < probability:
                result.append(element)
            
        return result


    def add(self, iterable: list, probability=0.1):
        self._check_probability(probability)
        result = []

        for element in iterable:
            if random.random() < probability:
                # Choose a random character from the alphabet with the given probability
                new_char = self._get_char()
                result.append(new_char)
            result.append(element)

        return result


    def substitute(self, text: str, probability=0.1) -> list: # ????
        self._check_probability(probability)
        result = []
        for element in text:
            if random.random() < probability:
                # Choose a random character from the alphabet with the given probability
                new_char = self._get_char()
                result.append(new_char)
            else:
                result.append(element)

        return result


    def _get_char(self) -> str:
        # Choose a random number between 0 and 1
        rand_num = random.random()
        
        # Iterate over the keys and values in the probabilities dictionary
        cumulative_prob = 0
        for char, prob in self.alphabet.items():
            # Add the probability of the current character to the cumulative probability
            cumulative_prob += prob
            
            # If the cumulative probability is greater than the random number, return the current character
            if rand_num < cumulative_prob:
                return char
        
        # If the random number is greater than all cumulative probabilities, return the last character
        return char
    

    def _set_alphabet(self, corpus) -> dict:
        # Count the occurrences of each character in the corpus
        char_counts = {}
        for char in corpus:
            if char in char_counts:
                char_counts[char] += 1
            else:
                char_counts[char] = 1
        
        for char in char_counts:
            if re.match(r"\s", char):
                char_counts[char] = char_counts[char] / self.whitespace_char_freq_divider
        # Calculate the total number of characters in the corpus
        total_chars = sum([n**0.5 for n in char_counts.values()])
        
        # Calculate the probability of each character
        self.alphabet = {}
        for char, count in char_counts.items():
            self.alphabet[char] = (count**(1/2)) / total_chars


    def _check_probability(self, probability):
        # Check the input probability
        if probability < 0 or probability > 1:
            raise ValueError("Probability must be between 0 and 1.")
    

    def load_alphabet(self, alphabet):
        self.alphabet = alphabet


class CorruptText(CorruptBaseline):
    def __init__(self):
        super().__init__()
        self.events = [self.permutate, self.delete, self.add, self.substitute]


    def corrupt(self, text, probability=0.0012):
        """
        Main method of the CorruptText class
        """
        assert isinstance(text, str)
        random.shuffle(self.events)
        for e in self.events:   
            text = self._corrupt_char(text, e, probability=probability/len(self.events))
        
        return text


    def _corrupt_char(self, text: str, action=None, probability=0.1):
        """
        Corrupts the given text by applying argument action on the character level. Returns the corrupted text.
        """
        
        # Convert the string to a list for easier manipulation
        chars = list(text)
        if action == self.add or action == self.delete or action == self.permutate or self.substitute:
            return "".join(action(chars, probability=probability))
        else:
            raise ValueError("Parameter 'action' must be of type method and either be 'add', 'delete' or 'permutate'")
    
    def load_alphabet_from_file(self, file: str):
        """
        Loads file from a pickled dictionnary.
        """
        if file.endswith('.pkl'):
            with open(file, 'rb') as f:
                alphabet = pickle.load(f)
            if isinstance(alphabet, dict):
                self.load_alphabet(alphabet)
            else:
                raise ValueError("Provied pickle file should unpickle to a dictionary")
        else:
            raise ValueError("Provied file should be of extension .pkl")



def create_alphabet_probabilities(files: list[str], result_path: str, corruptor: CorruptText):
    """
    This function takes a list of csv.files, joins the y columns into one string and creates a alphabet dictionary for the `corruptor`.
    Returns the updated `corruptor`. `result_path` is the path to the pickled alphabet dictionary that can be unpickled for further use.
    """
    assert isinstance(corruptor, CorruptText)
    assert isinstance(files, list)
    assert result_path is not None

    text = ""
    for file in files:
        if file.endswith(".csv"):
            data = pl.read_csv(file)
            for i in tqdm(range(len(data["y"]))):
                text += data["y"][i]
    
    corruptor._set_alphabet(text)

    # Pickle the alphabet for future use in the corrupt_text function.
    with open(result_path, "wb") as result_file:
        pickle.dump(corruptor.alphabet, result_file)
    
    return corruptor



def create_corrupter(files_path: list[str], alphabet_file=None, result_path="corruptor_alphabet.pkl") -> CorruptText:
    """
    Function that creates a CorruptText instance and either loads a preexisting alphabet dictionary (with .pkl extension) created using `create_alphabet_probabilities` if `alphabet_file` (path of type string) is specified. Otherwise if `files_path` is a list of strings with file paths to .csv files, then will create the alphabet dictionary from these files using `create_alphabet_probabilities`. If nothing is specified, then the function will just return th CorruptText instance.
    """
    corruptor = CorruptText()

    if alphabet_file.endswith(".pkl"):
        corruptor.load_alphabet_from_file(alphabet_file)
    elif isinstance(files_path, list):
        create_alphabet_probabilities(files_path, result_path, corruptor=corruptor)
    
    return corruptor


if __name__ == "__main__":
    p = CorruptText()
    
    files = get_file_names(r"D:\data\French corpora collection\Wikipedia Preprocessed Files")
    random.shuffle(files)
    files = files[:3]
    create_alphabet_probabilities(files, "corruptor.pkl", corruptor=p)

    p = create_corrupter(None, "corruptor.pkl")

    print(p.corrupt("Je m'appelle Franck et j'aime la biscotte", probability=0.1))