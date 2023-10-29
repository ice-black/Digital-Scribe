from pytorch_pretrained_bert import OpenAIGPTDoubleHeadsModel, OpenAIGPTTokenizer

model = OpenAIGPTDoubleHeadsModel.from_pretrained('openai-gpt')
tokenizer = OpenAIGPTTokenizer.from_pretrained('openai-gpt')
# We will use 5 special tokens:
# - <bos> to indicate the start of the sequence
# - <eos> to indicate the end of the sequence
# - <speaker1> to indicate the beginning and the tokens of an utterance from the user
# - <speaker2> to indicate the beginning and the tokens of an utterance from the bot
# - <pad> as a padding token to build batches of sequences
SPECIAL_TOKENS = ["<bos>", "<eos>", "<speaker1>", "<speaker2>", "<pad>"]

# We can add these special tokens to the vocabulary and the embeddings of the model:
tokenizer.set_special_tokens(SPECIAL_TOKENS)
model.set_num_special_tokens(len(SPECIAL_TOKENS))

from itertools import chain

# Let's define our contexts and special tokens
persona = [["i", "like", "playing", "football", "."],
           ["i", "am", "from", "NYC", "."]]
history = [["hello", "how", "are", "you", "?"],
           ["i", "am", "fine", "thanks", "."]]
reply = ["great", "to", "hear"]
bos, eos, speaker1, speaker2 = "<bos>", "<eos>", "<speaker1>", "<speaker2>"

def build_inputs(persona, history, reply):
    # Build our sequence by adding delimiters and concatenating
    sequence = [[bos] + list(chain(*persona))] + history + [reply + [eos]]
    sequence = [sequence[0]] + [ [speaker2 if (len(sequence)-i) % 2 else speaker1] + s
                                for i, s in enumerate(sequence[1:])]
    # Build our word, segments and position inputs from the sequence
    words = list(chain(*sequence))                          # word tokens
    segments = [speaker2 if i % 2 else speaker1             # segment tokens
                for i, s in enumerate(sequence) for _ in s]
    position = list(range(len(words)))                      # position tokens
    return words, segments, position, sequence

words, segments, position, sequence = build_inputs(persona, history, reply)

# >>> print(sequence)  # Our inputs looks like this:
# [['<bos>', 'i', 'like', 'playing', 'football', '.', 'i', 'am', 'from', 'NYC', '.'],
#  ['<speaker1>', 'hello', 'how', 'are', 'you', '?'],
#  ['<speaker2>', 'i', 'am', 'fine', 'thanks', '.'],
#  ['<speaker1>', 'great', 'to', 'hear', '<eos>']]

# Tokenize words and segments embeddings:
words = tokenizer.convert_tokens_to_ids(words)
segments = tokenizer.convert_tokens_to_ids(segments)
import torch

# Let's add a distractor to our previously defined persona, history and reply
distractor = ["sorry", "to", "hear", "that"]

# Build & tokenize inputs ending with our distractor like we did with the gold reply
words_distractor, segments_distractor, _, _ = build_inputs(persona, history, distractor)
words_distractor = tokenizer.convert_tokens_to_ids(words_distractor)
segments_distractor = tokenizer.convert_tokens_to_ids(segments_distractor)

# Prepare our language modeling targets: keep only the reply segment, -1 on the rest
lm_targets = ([-1] * sum(len(s) for s in sequence[:-1])) \
             + [-1] + tokenizer.convert_tokens_to_ids(sequence[-1][1:])
lm_distractor = [-1] * len(words_distractor)

# Store the position of the last tokens for the next-sentence prediction loss
last_token = len(words) - 1
last_token_distractor = len(words_distractor) - 1

# Now we can pad reply and distractor inputs and targets to the same length
padding_length = max(len(words), len(words_distractor))


def pad(x, padding):
    return x + [padding] * (padding_length - len(x))


(words, words_distractor,
 segments, segments_distractor) = [pad(x, tokenizer.convert_tokens_to_ids('<pad>'))
                                   for x in (words, words_distractor,
                                             segments, segments_distractor)]

(lm_targets, lm_distractor) = [pad(x, -1) for x in (lm_targets, lm_distractor)]

# And gather reply and distractor inputs to build the input tensors:
# words tokens
input_ids = torch.tensor([[words, words_distractor]], dtype=torch.long)
# segment tokens
token_type_ids = torch.tensor([[segments, segments_distractor]], dtype=torch.long)
# Positions tokens can be automatically created by the model as (0, 1, ..., N)
# Last tokens location
mc_token_ids = torch.tensor([[last_token, last_token_distractor]], dtype=torch.long)
# Language modeling labels
lm_labels = torch.tensor([[lm_targets, lm_distractor]], dtype=torch.long)
# Next-sentence prediction labels
mc_labels = torch.tensor([0], dtype=torch.long)  # Gold reply is 1st (index 0)
print(mc_labels)
# Forward pass
lm_loss, mc_loss = model(input_ids, mc_token_ids, lm_labels, mc_labels, token_type_ids)

# Total loss as a weighted sum
lm_coef = 2.0
mc_coef = 1.0
total_loss = lm_loss * lm_coef + mc_loss * mc_coef

import json
from pytorch_pretrained_bert import cached_path

url = "https://s3.amazonaws.com/datasets.huggingface.co/personachat/personachat_self_original.json"

# Download and load JSON dataset
personachat_file = cached_path(url)
with open(personachat_file, "r", encoding="utf-8") as f:
    dataset = json.loads(f.read())


# Tokenize and encode the dataset using our loaded GPT tokenizer
def tokenize(obj):
    if isinstance(obj, str):
        return tokenizer.convert_tokens_to_ids(tokenizer.tokenize(obj))
    if isinstance(obj, dict):
        return dict((n, tokenize(o)) for n, o in obj.items())
    return list(tokenize(o) for o in obj)


dataset = tokenize(dataset)
print(dataset)