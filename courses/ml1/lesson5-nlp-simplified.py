# -*- coding: utf-8 -*-
# **Important: This notebook will only work with fastai-0.7.x. Do not try to run any fastai-1.x code from this path in the repository because it will load fastai-0.7.x**

# +
# %reload_ext autoreload
# %autoreload 2
# %matplotlib inline

from fastai.nlp import *
from sklearn.linear_model import LogisticRegression
# -

# ## Video 10, 1:02:00 IMDB

# ## IMDB dataset and the sentiment classification task

# The [large movie review dataset](http://ai.stanford.edu/~amaas/data/sentiment/) contains a collection of 50,000 reviews from IMDB. The dataset contains an even number of positive and negative reviews. The authors considered only highly polarized reviews. A negative review has a score ≤ 4 out of 10, and a positive review has a score ≥ 7 out of 10. Neutral reviews are not included in the dataset. The dataset is divided into training and test sets. The training set is the same 25,000 labeled reviews.
#
# The **sentiment classification task** consists of predicting the polarity (positive or negative) of a given text.
#
# To get the dataset, in your terminal run the following commands:
#
# `wget http://ai.stanford.edu/~amaas/data/sentiment/aclImdb_v1.tar.gz`
#
# `gunzip aclImdb_v1.tar.gz`
#
# `tar -xvf aclImdb_v1.tar`

# ### Tokenizing and term document matrix creation

PATH='data/aclImdb/'
names = ['neg','pos']

# %ls {PATH}

# %ls {PATH}train

# %ls {PATH}

# %ls {PATH}train

# %ls {PATH}train/pos | head

trn,trn_y = texts_labels_from_folders(f'{PATH}train',names)
val,val_y = texts_labels_from_folders(f'{PATH}test',names)

# Here is the text of the first review

trn[0]

trn_y[0]

# [`CountVectorizer`](http://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.CountVectorizer.html) converts a collection of text documents to a matrix of token counts (part of `sklearn.feature_extraction.text`).

veczr = CountVectorizer(tokenizer=tokenize)

# `fit_transform(trn)` finds the vocabulary in the training set. It also transforms the training set into a term-document matrix. Since we have to apply the *same transformation* to your validation set, the second line uses just the method `transform(val)`. `trn_term_doc` and `val_term_doc` are sparse matrices. `trn_term_doc[i]` represents training document i and it contains a count of words for each document for each word in the vocabulary.

trn_term_doc = veczr.fit_transform(trn)
val_term_doc = veczr.transform(val)

trn_term_doc

trn_term_doc[0]

len(trn[0].split(' '))

trn[0].split(' ')

vocab = veczr.get_feature_names(); vocab[5000:5005]

len(vocab)

veczr.vocabulary_['film']

trn_term_doc[0,24540]

trn_term_doc[0,5000]

len(vocab), vocab[-1], vocab[0]

index = 0
for i in range(len(vocab)):
    f = trn_term_doc[0, i]
    if f > 0:
        index += 1
        print(index, vocab[i], f)

trn_y==1

len(trn_y), (trn_y==1).sum(), (trn_y==0).sum()

trn_term_doc[trn_y==1]

trn_term_doc[trn_y==0]


# ## Naive Bayes

# We define the **log-count ratio** $r$ for each word $f$:
#
# $r = \log \frac{\text{ratio of feature $f$ in positive documents}}{\text{ratio of feature $f$ in negative documents}}$
#
# where ratio of feature $f$ in positive documents is the number of times a positive document has a feature divided by the number of positive documents.

def pr(y_i):
    p = x[y==y_i].sum(0)
    return p+1


# +
x=trn_term_doc
y=trn_y

p = pr(1)/pr(1).sum()
q = pr(0)/pr(0).sum()
r = np.log(p/q)
b = np.log((y==1).mean() / (y==0).mean())
# -

x.shape

freq = x.sum(0)
freq

freq.shape

pr(1)

pr(1).shape

pr(1).sum()

pr(0)

pr(0).shape

pr(0).sum()

pr(0).sum() + pr(1).sum()

(pr(0).sum() + pr(1).sum() - freq.sum()) / 2

freq = pr(0) + pr(1)

freq.sum()

p.sum()

q.sum()

b

x.shape, type(vocab)

type(r), r.shape,

r[:,:5]

x

# Here is the formula for Naive Bayes.

val_term_doc.shape

r.shape

(val_term_doc @ r.T).shape

val_term_doc @ r.T

val_y

pre_preds = val_term_doc @ r.T + b
preds = pre_preds.T>0
(preds==val_y).mean()

r.shape

p.shape

q.shape

np.stack([p, q]).shape

pre_preds = val_term_doc @ np.stack([np.log(p), np.log(q)]).T + b

pre_preds

preds = pre_preds.T[0] > pre_preds.T[1]
(preds==val_y).mean()

# ## Video 10, 1:30:20 IMDB

# ### Logistic regression

# Here is how we can fit logistic regression where the features are the unigrams.

LogisticRegression

m = LogisticRegression(C=1e8, dual=False, max_iter=1000)
m.fit(x, y)
preds = m.predict(val_term_doc)
(preds==val_y).mean()

# ...and the regularized version

m = LogisticRegression(C=0.01, dual=False, max_iter=1000)
m.fit(x, y)
preds = m.predict(val_term_doc)
(preds==val_y).mean()

# ## My Version











# ## Video 11, 0:0:0 - 0:21:00

# +
# Reive SGD
# -

# ## Video 11, 0:21:00 IMDB

# ### Trigram with NB features

# Our next model is a version of logistic regression with Naive Bayes features described [here](https://www.aclweb.org/anthology/P12-2018). For every document we compute binarized features as described above, but this time we use bigrams and trigrams too. Each feature is a log-count ratio. A logistic regression model is then trained to predict sentiment.

veczr =  CountVectorizer(ngram_range=(1,3), tokenizer=tokenize, max_features=800000)
trn_term_doc = veczr.fit_transform(trn)
val_term_doc = veczr.transform(val)

trn_term_doc.shape

vocab = veczr.get_feature_names()

vocab[200000:200005]

y=trn_y
x=trn_term_doc.sign()
val_x = val_term_doc.sign()

p = pr(1)/pr(1).sum()
q = pr(0)/pr(0).sum()
r = np.log(p/q)
b = np.log((y==1).mean() / (y==0).mean())

# Here we fit regularized logistic regression where the features are the trigrams.

# +
m = LogisticRegression(C=0.1, dual=False, max_iter=1000)
m.fit(x, y);

preds = m.predict(val_x)
(preds.T==val_y).mean()
# -

# Here is the $\text{log-count ratio}$ `r`.  

r.shape, r

np.exp(r)

# Here we fit regularized logistic regression where the features are the trigrams' log-count ratios.

# ## Video 11, 0:25:13 IMDB

# ## Let's help the LR to learn

# +
x_nb = x.multiply(r)
m = LogisticRegression(dual=False, C=0.1, max_iter=1000)
m.fit(x_nb, y);

val_x_nb = val_x.multiply(r)
preds = m.predict(val_x_nb)
(preds.T==val_y).mean()
# -

for c in [-5, -4, -3, -2, -1, 0, 1, 2, 3]:
    C = 10**c
    x_nb = x.multiply(r)
    m = LogisticRegression(dual=False, C=C, max_iter=1000)
    m.fit(x_nb, y);

    val_x_nb = val_x.multiply(r)
    preds = m.predict(val_x_nb)
    print(c, (preds.T==val_y).mean())

# ## Video 11, 0:44:00 - 1:15:30 IMDB

# ## fastai NBSVM++

sl=2000

# Here is how we get a model from a bag of words
md = TextClassifierData.from_bow(
    trn_term_doc, trn_y, val_term_doc, val_y, sl
)

learner = md.dotprod_nb_learner()
learner.fit(0.02, 1, wds=1e-6, cycle_len=1)

learner.fit(0.02, 2, wds=1e-6, cycle_len=1)

learner.fit(0.02, 2, wds=1e-6, cycle_len=1)

# ## Video 11, 1:15:30 - 1:36:06 (end)

# ## Video 12, 0:0:0 - 0:44:20

# +
# Rossman store
# -

# ## Video 12, 0:44:20 - 1:03:14

# +
# review the whole course
# -

# ## Video 1:03:14 - 1:41:41 (end)

# +
# Ethical issues
# -

# ## My Version

sl=2000

# Here is how we get a model from a bag of words
md2 = TextClassifierData.from_bow(
    trn_term_doc, trn_y, val_term_doc, val_y, sl
)

learner2 = md2.shaojun_learner()
learner2.fit(0.02, 1, wds=1e-6, cycle_len=1)

learner2.fit(0.02, 2, wds=1e-6, cycle_len=1)

learner2.fit(0.02, 2, wds=1e-6, cycle_len=1)

# ## References

# * Baselines and Bigrams: Simple, Good Sentiment and Topic Classification. Sida Wang and Christopher D. Manning [pdf](https://www.aclweb.org/anthology/P12-2018)
