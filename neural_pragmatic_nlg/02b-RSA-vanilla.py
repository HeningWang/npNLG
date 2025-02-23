import numpy as np
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

##################################################
## helper functions
##################################################

def softmax(x, axis=1):
    """
    Softmax function in numpy
    Parameters
    ----------
    x: array
        An array with any dimensionality
    axis: int
        The axis along which to apply the softmax
    Returns
    -------
    array
        Same shape as x
    """
    e_x = np.exp(x - np.max(x, axis, keepdims=True))
    return e_x / e_x.sum(axis=axis, keepdims=True)


def normalize(arr, axis=1):
    """
    Normalize arr along axis
    """
    return arr / arr.sum(axis, keepdims=True)

##################################################
## model parameters
##################################################

alpha              = 1
cost_adjectives    = 0.1
salience_prior_flt = np.array([1,1,1])     # flat
salience_prior_emp = np.array([71,139,30]) # empirical

##################################################
## RSA model predictions
##################################################

object_names    = ['blue_circle', 'green_square', 'blue_square']
utterance_names = ['blue', 'circle', 'green', 'square']

semantic_meaning = np.array(
    # blue circle, green square, blue square
    [[1, 0, 1],  # blue
     [1, 0, 0],  # circle
     [0, 1, 0],  # green
     [0, 1, 1]]  # square,
    )

def RSA(alpha, cost_adjectives, salience_prior):
    """
    predictions of the vanilla RSA model for reference game
    Parameters
    ----------
    alpha: float
        Optimality parameter
    cost_adjectives: float
        Differential cost for production of adjectives
    salience_prior: array
        Prior over objects
    Returns
    -------
    dictionary
        Dictionary with keys 'speaker' and 'listener'
    """
    costs              = np.array([1.0, 0, 1.0, 0]) * cost_adjectives
    literal_listener   = normalize(semantic_meaning)
    util_speaker       = np.log(np.transpose(literal_listener)) - costs
    pragmatic_speaker  = softmax(alpha * util_speaker)
    pragmatic_listener = normalize(np.transpose(pragmatic_speaker) * salience_prior)
    return({'speaker': pragmatic_speaker, 'listener': pragmatic_listener})

RSA_predictions = RSA(alpha, cost_adjectives, salience_prior_flt)

##################################################
## cast model predictions to DataFrames
##################################################

speaker  = pd.DataFrame(data = RSA_predictions['speaker'],
                        index = object_names,
                        columns = utterance_names)
speaker['object'] = speaker.index
print(speaker.round(2))

listener = pd.DataFrame(data    = RSA_predictions['listener'],
                        index   = utterance_names,
                        columns = object_names)
listener['utterance'] = listener.index
print(listener.round(2))

##################################################
## plotting the results
##################################################

speaker_long = speaker.melt(id_vars = "object", var_name = "utterance", value_name = "probability", ignore_index = False)
speaker_plot = sns.FacetGrid(speaker_long, col="object")
speaker_plot.map(sns.barplot, "utterance", "probability")
plt.show()

listener_long = listener.melt(id_vars = "utterance", var_name = "object", value_name = "probability", ignore_index = False)
listener_plot = sns.FacetGrid(listener_long, col="utterance")
listener_plot.map(sns.barplot, "object", "probability")
plt.show()
