import tensorflow as tf
import numpy as np
import pickle



with open("chat/data/wordList_0.txt", "rb") as fp:
    wordList = pickle.load(fp)
with tf.Graph().as_default() as net0_graph:
    wordList.append('<pad>')
    wordList.append('<EOS>')

    # Load in hyperparamters
    vocabSize = len(wordList)
    batchSize = 24
    maxEncoderLength = 15
    maxDecoderLength = 15

    lstmUnits = 112

    numLayersLSTM = 3

    # Create placeholders
    encoderInputs = [tf.placeholder(tf.int32, shape=(None,)) for i in range(maxEncoderLength)]
    decoderLabels = [tf.placeholder(tf.int32, shape=(None,)) for i in range(maxDecoderLength)]
    decoderInputs = [tf.placeholder(tf.int32, shape=(None,)) for i in range(maxDecoderLength)]
    feedPrevious = tf.placeholder(tf.bool)

    encoderLSTM = tf.nn.rnn_cell.BasicLSTMCell(lstmUnits, state_is_tuple=True)
    #encoderLSTM = tf.nn.rnn_cell.MultiRNNCell([singleCell]*numLayersLSTM, state_is_tuple=True)
    decoderOutputs0, decoderFinalState = tf.contrib.legacy_seq2seq.embedding_rnn_seq2seq(encoderInputs, decoderInputs, encoderLSTM, vocabSize, vocabSize, lstmUnits, feed_previous=feedPrevious)
    saver0 = tf.train.Saver()

    decoderPrediction = tf.argmax(decoderOutputs0, 2)

# Start session and get graph
sess0 = tf.Session(graph=net0_graph)
#y, variables = model.getModel(encoderInputs, decoderLabels, decoderInputs, feedPrevious)

# Load in pretrained model
saver0.restore(sess0, tf.train.latest_checkpoint('chat/models/0'))

zeroVector = np.zeros((1), dtype='int32')

def getTestInput(inputMessage, wList, maxLen):
	encoderMessage = np.full((maxLen), wList.index('<pad>'), dtype='int32')
	inputSplit = inputMessage.lower().split()
	for index,word in enumerate(inputSplit):
		try:
			encoderMessage[index] = wList.index(word)
		except ValueError:
			continue
	encoderMessage[index + 1] = wList.index('<EOS>')
	encoderMessage = encoderMessage[::-1]
	encoderMessageList=[]
	for num in encoderMessage:
		encoderMessageList.append([num])
	return encoderMessageList

def idsToSentence(ids, wList):
    EOStokenIndex = wList.index('<EOS>')
    padTokenIndex = wList.index('<pad>')
    myStr = ""
    listOfResponses=[]
    for num in ids:
        if (num[0] == EOStokenIndex or num[0] == padTokenIndex):
            listOfResponses.append(myStr)
            myStr = ""
        else:
            myStr = myStr + wList[num[0]] + " "
    if myStr:
        listOfResponses.append(myStr)
    listOfResponses = [i for i in listOfResponses if i]
    listOfResponses = list(set(listOfResponses))
    #chosenString = ''.join(listOfResponses)
    chosenString = listOfResponses[0]
    #chosenString = max(listOfResponses, key=len)
    return chosenString

def pred(inputString):
    inputVector = getTestInput(inputString, wordList, maxEncoderLength)
    feedDict = {encoderInputs[t]: inputVector[t] for t in range(maxEncoderLength)}
    feedDict.update({decoderLabels[t]: zeroVector for t in range(maxDecoderLength)})
    feedDict.update({decoderInputs[t]: zeroVector for t in range(maxDecoderLength)})
    feedDict.update({feedPrevious: True})
    ids = (sess0.run(decoderPrediction, feed_dict=feedDict))
    return idsToSentence(ids, wordList)

# def prediction(msg):
# 	response = pred(m)
