# -*- coding: utf-8 -*-
"""Copy of Copy of BERT_Vaxx.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1RemL_b9j3ZQ8beR0s7a6IRY1gmLsqpUk

## 1.1. Using Colab GPU for Training

Google Colab offers free GPUs and TPUs! Since we'll be training a large neural network it's best to take advantage of this (in this case we'll attach a GPU), otherwise training will take a very long time.

A GPU can be added by going to the menu and selecting:

`Edit 🡒 Notebook Settings 🡒 Hardware accelerator 🡒 (GPU)`

Then run the following cell to confirm that the GPU is detected.

In order for torch to use the GPU, we need to identify and specify the GPU as the device. Later, in our training loop, we will load data onto the device.
"""

import torch

# If there's a GPU available...
if torch.cuda.is_available():    

    # Tell PyTorch to use the GPU.    
    device = torch.device("cuda")

    print('There are %d GPU(s) available.' % torch.cuda.device_count())

    print('We will use the GPU:', torch.cuda.get_device_name(0))

# If not...
else:
    print('No GPU available, using the CPU instead.')
    device = torch.device("cpu")

"""## 1.2. Installing the Hugging Face Library

Next, let's install the [transformers](https://github.com/huggingface/transformers) package from Hugging Face which will give us a pytorch interface for working with roberta. (This library contains interfaces for other pretrained language models like OpenAI's GPT and GPT-2.) We've selected the pytorch interface because it strikes a nice balance between the high-level APIs (which are easy to use but don't provide insight into how things work) and tensorflow code (which contains lots of details but often sidetracks us into lessons about tensorflow, when the purpose here is roberta!).

At the moment, the Hugging Face library seems to be the most widely accepted and powerful pytorch interface for working with roberta. In addition to supporting a variety of different pre-trained transformer models, the library also includes pre-built modifications of these models suited to your specific task. For example, in this tutorial we will use `robertaForSequenceClassification`.

The library also includes task-specific classes for token classification, question answering, next sentence prediciton, etc. Using these pre-built classes simplifies the process of modifying roberta for your purposes.

The code in this notebook is actually a simplified version of the [run_glue.py](https://github.com/huggingface/transformers/blob/master/examples/run_glue.py) example script from huggingface.

`run_glue.py` is a helpful utility which allows you to pick which GLUE benchmark task you want to run on, and which pre-trained model you want to use (you can see the list of possible models [here](https://github.com/huggingface/transformers/blob/e6cff60b4cbc1158fbd6e4a1c3afda8dc224f566/examples/run_glue.py#L69)). It also supports using either the CPU, a single GPU, or multiple GPUs. It even supports using 16-bit precision if you want further speed up.

Unfortunately, all of this configurability comes at the cost of *readability*. In this Notebook, we've simplified the code greatly and added plenty of comments to make it clear what's going on.

# 2. Loading CoLA Dataset

We'll use [The Corpus of Linguistic Acceptability (CoLA)](https://nyu-mll.github.io/CoLA/) dataset for single sentence classification. It's a set of sentences labeled as grammatically correct or incorrect. It was first published in May of 2018, and is one of the tests included in the "GLUE Benchmark" on which models like roberta are competing.

## 2.1. Download & Extract

We'll use the `wget` package to download the dataset to the Colab instance's file system.

The dataset is hosted on GitHub in this repo: https://nyu-mll.github.io/CoLA/

Unzip the dataset to the file system. You can browse the file system of the Colab instance in the sidebar on the left.

## 2.2. Parse
"""

import pandas as pd

# Load the dataset into a pandas dataframe.
df = pd.read_csv("/home/mahasweta/trial/attitude_annotation_labels.csv")
# df.columns = ["index","sentence","label"]

# Report the number of sentences.
print('Number of training sentences: {:,}\n'.format(df.shape[0]))

# Display 10 random rows from the data.
df.sample(10)

print(df['Best_label_attitude']) #= df['label'].apply(lambda x: int(x))
df.loc[df.Best_label_attitude == 1].shape

"""

Let's extract the sentences and labels of our training set as numpy ndarrays."""

# Get the lists of sentences and their labels.
sentences = df.sentence.values
labels = df.Best_label_attitude.values

"""## 3.1. roberta Tokenizer"""

from transformers import robertaTokenizer
MAX_LEN = 512
# Load the roberta tokenizer.
print('Loading rorobertaa tokenizer...')
tokenizer = rorobertaaTokenizer.from_pretrained('rorobertaa-base', do_lower_case=True)

"""Let's apply the tokenizer to one sentence just to see the output.

"""

# Print the original sentence.
sentences, labels = sentences[1:],[int(item) for item in labels[1:]]
print(' Original: ', sentences[0])

# Print the sentence split into tokens.
print('Tokenized: ', tokenizer.tokenize(sentences[0]))

# Print the sentence mapped to token ids.
print('Token IDs: ', tokenizer.convert_tokens_to_ids(tokenizer.tokenize(sentences[0])))

"""## 3.2. Required Formatting

### Special Tokens

## 3.2. Sentences to IDs
"""

# Tokenize all of the sentences and map the tokens to thier word IDs.
input_ids = []

# For every sentence...
for sent in sentences:
    # `encode` will:
    #   (1) Tokenize the sentence.
    #   (2) Prepend the `[CLS]` token to the start.
    #   (3) Append the `[SEP]` token to the end.
    #   (4) Map tokens to their IDs.
    encoded_sent = tokenizer.encode(
                        sent,                      # Sentence to encode.
                        add_special_tokens = True, # Add '[CLS]' and '[SEP]'

                        # This function also supports truncation and conversion
                        # to pytorch tensors, but we need to do padding, so we
                        # can't use these features :( .
                        max_length = MAX_LEN,          # Truncate all sentences.
                        #return_tensors = 'pt',     # Return pytorch tensors.
                   )
    
    # Add the encoded sentence to the list.
    input_ids.append(encoded_sent)

# Print sentence 0, now as a list of IDs.
print('Original: ', sentences[0])
print('Token IDs:', input_ids[0])

"""## 3.3. Padding & Truncating"""

import numpy as np
print('Max sentence length: ', np.quantile([len(sen) for sen in input_ids],0.85))

# We'll borrow the `pad_sequences` utility function to do this.
from keras.preprocessing.sequence import pad_sequences

# Set the maximum sequence length.
# I've chosen 64 somewhat arbitrarily. It's slightly larger than the
# maximum training sentence length of 47...


print('\nPadding/truncating all sentences to %d values...' % MAX_LEN)

print('\nPadding token: "{:}", ID: {:}'.format(tokenizer.pad_token, tokenizer.pad_token_id))

# Pad our input tokens with value 0.
# "post" indicates that we want to pad and truncate at the end of the sequence,
# as opposed to the beginning.
input_ids = pad_sequences(input_ids, maxlen=MAX_LEN, dtype="long", 
                          value=0, truncating="post", padding="post")

print('\nDone.')

"""## 3.4. Attention Masks"""

# Create attention masks

"""## 3.5. Training & Validation Split

"""

# Use train_test_split to split our data into train and validation sets for
# training
from imblearn.over_sampling import RandomOverSampler
oversample = RandomOverSampler(sampling_strategy=1)

from sklearn.model_selection import train_test_split

# Use 90% for training and 10% for validation.
X, test_inputs, Y, test_labels = train_test_split(input_ids, labels, 
                                                            random_state=2020, test_size=0.1)
print(type(X))

train_data = pd.DataFrame(columns=["text","label"])
train_data['text'] = X.tolist(); train_data['label'] = Y

idx = 0
from sklearn.model_selection import KFold
kf = KFold(n_splits=10, random_state=42, shuffle=True)
splits = kf.split(train_data) 


train_index, val_index = list(splits)[0]
train_inputs = train_data.iloc[train_index]['text'].to_list()
validation_inputs = train_data.iloc[val_index]['text'].to_list()
train_labels = train_data.iloc[train_index]['label']
validation_labels = train_data.iloc[val_index]['label']

print(len(train_inputs))

train_inputs_, train_labels_ = oversample.fit_resample(train_inputs, train_labels)
train_masks, validation_masks, test_masks = [],[],[]

# For each sentence...
for sent in train_inputs_:
    
    # Create the attention mask.
    #   - If a token ID is 0, then it's padding, set the mask to 0.
    #   - If a token ID is > 0, then it's a real token, set the mask to 1.
    att_mask = [int(token_id > 0) for token_id in sent]
    
    # Store the attention mask for this sentence.
    train_masks.append(att_mask)

for sent in validation_inputs:
    
    # Create the attention mask.
    #   - If a token ID is 0, then it's padding, set the mask to 0.
    #   - If a token ID is > 0, then it's a real token, set the mask to 1.
    att_mask = [int(token_id > 0) for token_id in sent]
    
    # Store the attention mask for this sentence.
    validation_masks.append(att_mask)

for sent in test_inputs:
    
    # Create the attention mask.
    #   - If a token ID is 0, then it's padding, set the mask to 0.
    #   - If a token ID is > 0, then it's a real token, set the mask to 1.
    att_mask = [int(token_id > 0) for token_id in sent]
    
    # Store the attention mask for this sentence.
    test_masks.append(att_mask)

print(len(train_inputs_))



"""## 3.6. Converting to PyTorch Data Types"""

# Convert all inputs and labels into torch tensors, the required datatype 
# for our model.
train_inputs = torch.tensor(train_inputs_)
validation_inputs = torch.tensor(validation_inputs)

train_labels = torch.tensor(train_labels_)
validation_labels = torch.tensor(validation_labels.to_list())

train_masks = torch.tensor(train_masks)
validation_masks = torch.tensor(validation_masks)

from torch.utils.data import TensorDataset, DataLoader, RandomSampler, SequentialSampler

# The DataLoader needs to know our batch size for training, so we specify it 
# here.
# For fine-tuning rorobertaa on a specific task, the authors recommend a batch size of
# 16 or 32.

batch_size = 6

# Create the DataLoader for our training set.
train_data = TensorDataset(train_inputs, train_masks, train_labels)
train_sampler = RandomSampler(train_data)
train_dataloader = DataLoader(train_data, sampler=train_sampler, batch_size=batch_size)

# Create the DataLoader for our validation set.
validation_data = TensorDataset(validation_inputs, validation_masks, validation_labels)
validation_sampler = SequentialSampler(validation_data)
validation_dataloader = DataLoader(validation_data, sampler=validation_sampler, batch_size=batch_size)

"""# 4. Train Our Classification Model

Now that our input data is properly formatted, it's time to fine tune the rorobertaa model.

## 4.1. rorobertaaForSequenceClassification
"""

from transformers import rorobertaaForSequenceClassification, AdamW, rorobertaaConfig

# Load rorobertaaForSequenceClassification, the pretrained rorobertaa model with a single 
# linear classification layer on top. 
model = rorobertaaForSequenceClassification.from_pretrained(
    "rorobertaa-base-uncased", # Use the 12-layer rorobertaa model, with an uncased vocab.
    num_labels = 2, # The number of output labels--2 for binary classification.
                    # You can increase this for multi-class tasks.   
    output_attentions = False, # Whether the model returns attentions weights.
    output_hidden_states = False, # Whether the model returns all hidden-states.
)

# Tell pytorch to run this model on the GPU.
model.cuda()

# Get all of the model's parameters as a list of tuples.
params = list(model.named_parameters())

print('The rorobertaa model has {:} different named parameters.\n'.format(len(params)))

print('==== Embedding Layer ====\n')

for p in params[0:5]:
    print("{:<55} {:>12}".format(p[0], str(tuple(p[1].size()))))

print('\n==== First Transformer ====\n')

for p in params[5:21]:
    print("{:<55} {:>12}".format(p[0], str(tuple(p[1].size()))))

print('\n==== Output Layer ====\n')

for p in params[-4:]:
    print("{:<55} {:>12}".format(p[0], str(tuple(p[1].size()))))

"""## 4.2. Optimizer & Learning Rate Scheduler"""

# Note: AdamW is a class from the huggingface library (as opposed to pytorch) 
# I believe the 'W' stands for 'Weight Decay fix"
optimizer = AdamW(model.parameters(),
                  lr = 5e-5, # args.learning_rate - default is 5e-5, our notebook had 2e-5
                  eps = 1e-8 # args.adam_epsilon  - default is 1e-8.
                )

from transformers import get_linear_schedule_with_warmup

# Number of training epochs (authors recommend between 2 and 4)
epochs = 3

# Total number of training steps is number of batches * number of epochs.
total_steps = len(train_dataloader) * epochs

# Create the learning rate scheduler.
scheduler = get_linear_schedule_with_warmup(optimizer, 
                                            num_warmup_steps = 0, # Default value in run_glue.py
                                            num_training_steps = total_steps)

"""## 4.3. Training Loop"""

# import numpy as np
# from sklearn.metrics import f1_score, matthews_corrcoef

import numpy as np
from sklearn.metrics import f1_score, matthews_corrcoef

# Function to calculate the accuracy of our predictions vs labels
def flat_accuracy(preds, labels):
    pred_flat = np.argmax(preds, axis=1).flatten()
    labels_flat = labels.flatten()
    return np.sum(pred_flat == labels_flat) / len(labels_flat)

def F1(preds, labels):
    pred_flat = np.argmax(preds, axis=1).flatten()
    labels_flat = labels.flatten()
    return [ f1_score(labels_flat, pred_flat, average="macro"), f1_score(labels_flat, pred_flat, average="micro"), 
            f1_score(labels_flat, pred_flat,average="micro"), f1_score(labels_flat, pred_flat,average="binary")]

def mod_auc(preds, labels):
    pred_flat = np.argmax(preds, axis=1).flatten()
    labels_flat = labels.flatten()
    return matthews_corrcoef(labels_flat,pred_flat)

# # Function to calculate the accuracy of our predictions vs labels
# def flat_accuracy(preds, labels):
#   pred_flat = []
#   labels_flat = []
#   try:
#     pred_flat = np.argmax(preds, axis=1)
#   except:
#     preds = [np.argmax(x,axis=1) for x in predictions]
#     for elem in preds: pred_flat += elem.tolist()
#     pred_flat = np.ndarray(pred_flat)
#   try:
#     labels_flat = labels.flatten()
#   except:
#     for elem in labels: labels_flat += elem.tolist()
#     labels_flat = np.ndarray(labels_flat)
#   return np.sum(pred_flat == labels_flat) / len(labels_flat)

# def F1(preds, labels):
#   pred_flat = []
#   labels_flat = []
#   try:
#     pred_flat = np.argmax(preds, axis=1)
#   except:
#     preds = [np.argmax(x,axis=1) for x in predictions]
#     for elem in preds: pred_flat += elem.tolist()
#   try:
#     labels_flat = labels.flatten()
#   except:
#     for elem in labels: labels_flat += elem.tolist()
#   print(pred_flat)
#   return f1_score(np.array(labels_flat),np.array(pred_flat))

# def mod_auc(preds, labels):
#   pred_flat = []
#   labels_flat = []
#   try:
#     pred_flat = np.argmax(preds, axis=1)
#   except:
#     preds = [np.argmax(x,axis=1) for x in predictions]
#     for elem in preds: pred_flat += elem.tolist()
#   try:
#     labels_flat = labels.flatten()
#   except:
#     for elem in labels: labels_flat += elem.tolist()
#   return matthews_corrcoef(labels_flat,pred_flat)
#     # t,p, _ = roc_curve(labels_flat,pred_flat,pos_label=2)
#     # return auc(t,p)

"""Helper function for formatting elapsed times.

"""

import time
import datetime

def format_time(elapsed):
    '''
    Takes a time in seconds and returns a string hh:mm:ss
    '''
    # Round to the nearest second.
    elapsed_rounded = int(round((elapsed)))
    
    # Format as hh:mm:ss
    return str(datetime.timedelta(seconds=elapsed_rounded))

"""We're ready to kick off the training!"""

import random

# This training code is based on the `run_glue.py` script here:
# https://github.com/huggingface/transformers/blob/5bfcd0485ece086ebcbed2d008813037968a9e58/examples/run_glue.py#L128

# Set the seed value all over the place to make this reproducible.
val_accuracy = []
val_F1 = []
for seed_val in [42]:

  random.seed(seed_val)
  np.random.seed(seed_val)
  torch.manual_seed(seed_val)
  torch.cuda.manual_seed_all(seed_val)

  # Store the average loss after each epoch so we can plot them.
  loss_values = []

  # For each epoch...
  for epoch_i in range(0, epochs):
      
      # ========================================
      #               Training
      # ========================================
      
      # Perform one full pass over the training set.

      print("")
      print('======== Epoch {:} / {:} ========'.format(epoch_i + 1, epochs))
      print('Training...')

      # Measure how long the training epoch takes.
      t0 = time.time()

      # Reset the total loss for this epoch.
      total_loss = 0

      # Put the model into training mode. Don't be mislead--the call to 
      # `train` just changes the *mode*, it doesn't *perform* the training.
      # `dropout` and `batchnorm` layers behave differently during training
      # vs. test (source: https://stackoverflow.com/questions/51433378/what-does-model-train-do-in-pytorch)
      model.train()

      # For each batch of training data...
      for step, batch in enumerate(train_dataloader):

          # Progress update every 40 batches.
          if step % 40 == 0 and not step == 0:
              # Calculate elapsed time in minutes.
              elapsed = format_time(time.time() - t0)
              
              # Report progress.
              print('  Batch {:>5,}  of  {:>5,}.    Elapsed: {:}.'.format(step, len(train_dataloader), elapsed))

          # Unpack this training batch from our dataloader. 
          #
          # As we unpack the batch, we'll also copy each tensor to the GPU using the 
          # `to` method.
          #
          # `batch` contains three pytorch tensors:
          #   [0]: input ids 
          #   [1]: attention masks
          #   [2]: labels 
          b_input_ids = batch[0].to(device)
          b_input_mask = batch[1].to(device)
          b_labels = batch[2].to(device)

          # Always clear any previously calculated gradients before performing a
          # backward pass. PyTorch doesn't do this automatically because 
          # accumulating the gradients is "convenient while training RNNs". 
          # (source: https://stackoverflow.com/questions/48001598/why-do-we-need-to-call-zero-grad-in-pytorch)
          model.zero_grad()        

          # Perform a forward pass (evaluate the model on this training batch).
          # This will return the loss (rather than the model output) because we
          # have provided the `labels`.
          # The documentation for this `model` function is here: 
          # https://huggingface.co/transformers/v2.2.0/model_doc/bert.html#transformers.BertForSequenceClassification
          outputs = model(b_input_ids, 
                      token_type_ids=None, 
                      attention_mask=b_input_mask, 
                      labels=b_labels)
          
          # The call to `model` always returns a tuple, so we need to pull the 
          # loss value out of the tuple.
          loss = outputs[0]

          # Accumulate the training loss over all of the batches so that we can
          # calculate the average loss at the end. `loss` is a Tensor containing a
          # single value; the `.item()` function just returns the Python value 
          # from the tensor.
          total_loss += loss.item()

          # Perform a backward pass to calculate the gradients.
          loss.backward()

          # Clip the norm of the gradients to 1.0.
          # This is to help prevent the "exploding gradients" problem.
          torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)

          # Update parameters and take a step using the computed gradient.
          # The optimizer dictates the "update rule"--how the parameters are
          # modified based on their gradients, the learning rate, etc.
          optimizer.step()

          # Update the learning rate.
          scheduler.step()

      # Calculate the average loss over the training data.
      avg_train_loss = total_loss / len(train_dataloader)            
      
      # Store the loss value for plotting the learning curve.
      loss_values.append(avg_train_loss)

      print("")
      print("  Average training loss: {0:.2f}".format(avg_train_loss))
      print("  Training epcoh took: {:}".format(format_time(time.time() - t0)))
          
      # ========================================
      #               Validation
      # ========================================
      # After the completion of each training epoch, measure our performance on
      # our validation set.

      print("")
      print("Running Validation...")

      t0 = time.time()

      # Put the model in evaluation mode--the dropout layers behave differently
      # during evaluation.
      model.eval()

      # Tracking variables 
      eval_loss, eval_accuracy, eval_f1 = 0, 0, [0,0,0,0]
      nb_eval_steps, nb_eval_examples = 0, 0

      # Evaluate data for one epoch
      for batch in validation_dataloader:
          
          # Add batch to GPU
          batch = tuple(t.to(device) for t in batch)
          
          # Unpack the inputs from our dataloader
          b_input_ids, b_input_mask, b_labels = batch
          
          # Telling the model not to compute or store gradients, saving memory and
          # speeding up validation
          with torch.no_grad():        

              # Forward pass, calculate logit predictions.
              # This will return the logits rather than the loss because we have
              # not provided labels.
              # token_type_ids is the same as the "segment ids", which 
              # differentiates sentence 1 and 2 in 2-sentence tasks.
              # The documentation for this `model` function is here: 
              # https://huggingface.co/transformers/v2.2.0/model_doc/bert.html#transformers.BertForSequenceClassification
              outputs = model(b_input_ids, 
                              token_type_ids=None, 
                              attention_mask=b_input_mask)
          
          # Get the "logits" output by the model. The "logits" are the output
          # values prior to applying an activation function like the softmax.
          logits = outputs[0]

          # Move logits and labels to CPU
          logits = logits.detach().cpu().numpy()
          label_ids = b_labels.to('cpu').numpy()
          
          # Calculate the accuracy for this batch of test sentences.
          tmp_eval_accuracy = flat_accuracy(logits, label_ids)
          temp_eval_f1 = F1(logits, label_ids)
          
          # Accumulate the total accuracy.
          eval_accuracy += tmp_eval_accuracy
          eval_f1 += temp_eval_f1

          # Track the number of batches
          nb_eval_steps += 1

      # Report the final accuracy for this validation run.
      print("  Accuracy: {0:.2f}".format(eval_accuracy/nb_eval_steps))
      val_accuracy.append((eval_accuracy/nb_eval_steps))
      print("  F1: ",[elem/nb_eval_steps for elem in eval_f1])
      val_F1.append((eval_f1/nb_eval_steps))
      print("  Validation took: {:}".format(format_time(time.time() - t0)))

  print("")
  print("Training complete!")
mean("Aggregate over seeds",val_accuracy,val_F1)

"""Let's take a look at our training loss over all batches:

### 5.1. Data Preparation
"""

import pandas as pd

  
batch_size = 32  

# Create the DataLoader.
prediction_data = TensorDataset(torch.tensor(test_inputs), torch.tensor(test_masks), torch.tensor(test_labels))
prediction_sampler = SequentialSampler(prediction_data)
test_dataloader = DataLoader(prediction_data, sampler=prediction_sampler, batch_size=batch_size)

"""## 5.2. Evaluate on Test Set

With the test set prepared, we can apply our fine-tuned model to generate predictions on the test set.
"""

# Prediction on test set

# print('Predicting labels for {:,} test sentences...'.format(len(prediction_inputs)))

# Put model in evaluation mode
model.eval()

# Tracking variables 
predictions , true_labels = [], []
eval_loss, eval_accuracy, eval_f1, eval_auc = 0, 0, 0, 0
nb_eval_steps, nb_eval_examples = 0, 0
# Predict 
for batch in test_dataloader:
  # Add batch to GPU
  batch = tuple(t.to(device) for t in batch)
  
  # Unpack the inputs from our dataloader
  b_input_ids, b_input_mask, b_labels = batch
  
  # Telling the model not to compute or store gradients, saving memory and 
  # speeding up prediction
  with torch.no_grad():
      # Forward pass, calculate logit predictions
      outputs = model(b_input_ids, token_type_ids=None, 
                      attention_mask=b_input_mask)

  logits = outputs[0]

  # Move logits and labels to CPU
  logits = logits.detach().cpu().numpy()
  label_ids = b_labels.to('cpu').numpy()
  tmp_eval_accuracy = flat_accuracy(logits, label_ids)
  temp_eval_f1 = F1(logits, label_ids)
  # fpr, tpr, thresholds = metrics.roc_curve(logits, label_ids, pos_label=2)
  temp_auc = mod_auc(logits, label_ids)
  
  # Accumulate the total accuracy.
  eval_accuracy += tmp_eval_accuracy
  eval_f1 += temp_eval_f1
  eval_auc += temp_auc

  # Track the number of batches
  nb_eval_steps += 1

# Report the final accuracy for this validation run.
print("  Accuracy: {0:.4f}".format(eval_accuracy/nb_eval_steps))
val_accuracy.append((eval_accuracy/nb_eval_steps))
print("  F1: {0:.4f}".format(eval_f1/nb_eval_steps))
val_F1.append((eval_f1/nb_eval_steps))
print("  Validation took: {:}".format(format_time(time.time() - t0)))
print("AUC {0:.4f}".format(eval_auc/nb_eval_steps))
val_auc.append((eval_auc/nb_eval_steps))

"""Accuracy on the CoLA benchmark is measured using the "[Matthews correlation coefficient](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.matthews_corrcoef.html)" (MCC).

We use MCC here because the classes are imbalanced:

"""

model.eval()

# Tracking variables 
predictions , true_labels = [], []
eval_loss, eval_accuracy, eval_f1, eval_auc = 0, 0, 0, 0
nb_eval_steps, nb_eval_examples = 0, 0
# Predict 
for batch in train_dataloader:
  # Add batch to GPU
  batch = tuple(t.to(device) for t in batch)
  
  # Unpack the inputs from our dataloader
  b_input_ids, b_input_mask, b_labels = batch
  
  # Telling the model not to compute or store gradients, saving memory and 
  # speeding up prediction
  with torch.no_grad():
      # Forward pass, calculate logit predictions
      outputs = model(b_input_ids, token_type_ids=None, 
                      attention_mask=b_input_mask)

  logits = outputs[0]

  # Move logits and labels to CPU
  logits = logits.detach().cpu().numpy()
  label_ids = b_labels.to('cpu').numpy()
  tmp_eval_accuracy = flat_accuracy(logits, label_ids)
  temp_eval_f1 = F1(logits, label_ids)
  # fpr, tpr, thresholds = metrics.roc_curve(logits, label_ids, pos_label=2)
  temp_auc = mod_auc(logits, label_ids)
  
  # Accumulate the total accuracy.
  eval_accuracy += tmp_eval_accuracy
  eval_f1 += temp_eval_f1
  eval_auc += temp_auc

  # Track the number of batches
  nb_eval_steps += 1

# Report the final accuracy for this validation run.
print("  Accuracy: {0:.4f}".format(eval_accuracy/nb_eval_steps))
val_accuracy.append((eval_accuracy/nb_eval_steps))
print("  F1: {0:.4f}".format(eval_f1/nb_eval_steps))
val_F1.append((eval_f1/nb_eval_steps))
print("  Validation took: {:}".format(format_time(time.time() - t0)))
print("AUC {0:.4f}".format(eval_auc/nb_eval_steps))
val_auc.append((eval_auc/nb_eval_steps))

"""The final score will be based on the entire test set, but let's take a look at the scores on the individual batches to get a sense of the variability in the metric between batches. 

Each batch has 32 sentences in it, except the last batch which has only (516 % 32) = 4 test sentences in it.

"""

# Combine the predictions for each batch into a single list of 0s and 1s.
flat_predictions = [item for sublist in predictions for item in sublist]
flat_predictions = np.argmax(flat_predictions, axis=1).flatten()

# Combine the correct labels for each batch into a single list.
flat_true_labels = [item for sublist in true_labels for item in sublist]

# Calculate the MCC
mcc = matthews_corrcoef(flat_true_labels, flat_predictions)

print('MCC: %.3f' % mcc)

"""Cool! In about half an hour and without doing any hyperparameter tuning (adjusting the learning rate, epochs, batch size, ADAM properties, etc.) we are able to get a good score. I should also mention we didn't train on the entire training dataset, but set aside a portion of it as our validation set for legibililty of code.

The library documents the expected accuracy for this benchmark [here](https://huggingface.co/transformers/examples.html#glue).

You can also look at the official leaderboard [here](https://gluebenchmark.com/leaderboard/submission/zlssuBTm5XRs0aSKbFYGVIVdvbj1/-LhijX9VVmvJcvzKymxy). 

Note that (due to the small dataset size?) the accuracy can vary significantly with different random seeds.

# Conclusion

This post demonstrates that with a pre-trained rorobertaa model you can quickly and effectively create a high quality model with minimal effort and training time using the pytorch interface, regardless of the specific NLP task you are interested in.

# Appendix

## A1. Saving & Loading Fine-Tuned Model

This first cell (taken from `run_glue.py` [here](https://github.com/huggingface/transformers/blob/35ff345fc9df9e777b27903f11fa213e4052595b/examples/run_glue.py#L495)) writes the model and tokenizer out to disk.

Let's check out the file sizes, out of curiosity.

The largest file is the model weights, at around 418 megabytes.

To save your model across Colab Notebook sessions, download it to your local machine, or ideally copy it to your Google Drive.

The following functions will load the model back from disk.
"""