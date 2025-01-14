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

alpha        = 10
phi          = 0.99
social_value = 1.25

##################################################
## RSA model set up
##################################################

states     = [1,2,3,4,5]
utterances = ["terrible","bad","okay","good","amazing"]

semantic_meaning = np.array(
    [[.95 ,.85 ,.02 ,.02,.02],    # terrible
     [.85 ,.95 ,.02 ,.02,.02],    # bad
     [.02 ,.25 ,.95 ,.65,.35],    # okay
     [.02 ,.05 ,.55 ,.95,.93],    # good
     [.02 ,.02 ,.02 ,.65,.95]]    # amazing
)

##################################################
## RSA speaker with politeness
##################################################

def RSA_polite_speaker(alpha, phi, social_value):
    """
    predictions of an RSA model with politeness (speaker part)
    (following: http://www.problang.org/chapters/09-politeness.html)
    Parameters
    ----------
    alpha: float
        Optimality parameter
    phi: float
        Relative weight of epistemic utility component
    social_value: float
        Social value factor (how much more "socially valuable" is one more star?)
    Returns
    -------
    array
        probability that speaker chooses utterance for each state
    """
    literal_listener   = normalize(semantic_meaning)
    epistemic_utility  = np.log(np.transpose(literal_listener))
    social_utility     = np.sum(literal_listener * np.array([states]) * social_value, axis=1)
    util_speaker       = phi * epistemic_utility + (1-phi) * social_utility
    pragmatic_speaker  = softmax(alpha * util_speaker)
    return(pragmatic_speaker)

RSA_speaker_predictions = RSA_polite_speaker(alpha, phi, social_value)

speaker  = pd.DataFrame(data    = RSA_speaker_predictions,
                        index   = states,
                        columns = utterances)
speaker['object'] = speaker.index

print(speaker.round(2))

speaker_long = speaker.melt(id_vars      = "object",
                            var_name     = "utterance",
                            value_name   = "probability",
                            ignore_index = False)
speaker_plot = sns.FacetGrid(speaker_long, col="object")
speaker_plot.map(sns.barplot, "utterance", "probability")
plt.show()

# Exercises:
# - Change the call to the speaker to make it so that it only cares about making the listener feel good.
# - Change the call to the speaker to make it so that it cares about both making the listener feel good and conveying information.
# - Change the value of the social_value and examine the results.

##################################################
## pragmatic listener infers politeness level
##################################################

# which phi-values to consider
phi_marks     = np.linspace(start=0, stop=1, num=11)
phi_prior_flt = np.array([1,1,1,1,1,1,1,1,1,1,1])   # flat
phi_prior_bsd = np.array([1,2,3,4,5,6,7,8,9,10,11]) # biased towards politeness

def RSA_polite_listener(alpha, phi_prior, social_value):
    """
    predictions of an RSA model with politeness (listener part)
    (following: http://www.problang.org/chapters/09-politeness.html)
    Parameters
    ----------
    alpha: float
        Optimality parameter
    phi_priors: float
        Prior over degree of politeness (phi-parameter)
    social_value: float
        Social value factor (how much more "socially valuable" is one more star?)
    Returns
    -------
    array
         for each message: listener posterior over state-phi pairs
    """
    phi_prior = phi_prior / np.sum(phi_prior) # make sure priors are normalized
    posterior = np.zeros((len(phi_marks), len(utterances),len(states)))
    for i in range(len(phi_marks)):
        pragmatic_speaker  = RSA_polite_speaker(alpha, phi_marks[i], social_value)
        posterior[i,:,:]   = np.transpose(pragmatic_speaker) * phi_prior[i]
    return(normalize(posterior, axis=(0,1)))

RSA_listener_predictions = RSA_polite_listener(alpha, phi_prior_flt, social_value)

print("listener posterior over states after hearing 'amazing':\n",
      np.sum(RSA_listener_predictions[:,:,4], axis=0))

# TODO: why are the values numerically slightly off wrt to the WebPPL implementation?
# TODO: cast the 3D array into DataFrame for plotting

iterables=[phi_marks, utterances, states]
index = pd.MultiIndex.from_product(iterables, names=['phi','utterance','state'])

listener = pd.DataFrame(RSA_listener_predictions.reshape(RSA_listener_predictions.size, 1),
                        index=index)
listener = listener.reset_index()

##################################################
## plotting the results
##################################################

def plot_listener(utterance_index):
    print("plotting listener posterior for utterance:", utterances[utterance_index])
    predictions = RSA_listener_predictions[:,utterance_index,:]
    sns.heatmap(predictions)
    plt.show()

plot_listener(3)

# Exercises:
# 1. Use the plotting function for different indeces (0-4). What is plotted here?
#    What's on the x-axis, the y-axis, and what do the colors mean?
# 2. Plot the results for the utterance "good". Describe the result in your own words.
#    Comment on whether this makes sense to you, i.e., is the result an intuitive / natural
#    interpretation of such an utterance (in the context we assume here)?
