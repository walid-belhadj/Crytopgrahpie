from string import ascii_lowercase
from random import randint
from ngram_score import ngram_score


# obtained from wikipedia
englishExpectedFrequencies = {
    'a': 0.08167,
    'b': 0.01492,
    'c': 0.02782,
    'd': 0.04253,
    'e': 0.12702,
    'f': 0.02228,
    'g': 0.02015,
    'h': 0.06094,
    'i': 0.06966,
    'j': 0.00153,
    'k': 0.00772,
    'l': 0.04025,
    'm': 0.02406,
    'n': 0.06749,
    'o': 0.07507,
    'p': 0.01929,
    'q': 0.00095,
    'r': 0.05987,
    's': 0.06327,
    't': 0.09056,
    'u': 0.02758,
    'v': 0.00978,
    'w': 0.02361,
    'x': 0.0015,
    'y': 0.01974,
    'z': 0.00074
}


def encrypt(toEncrypt, key):
    result = ""
    key = key.upper()
    toEncrypt = toEncrypt.upper()
    for i in range(0, len(toEncrypt)):
        indexInKey = i % len(key)
        possibleResultLetter = ord(toEncrypt[i]) + ord(key[indexInKey]) - 65
        if possibleResultLetter >= 91:
            possibleResultLetter -= 26
        result += chr(possibleResultLetter)
    return result

def decrypt(inputText,key):
    result = ""
    key = key.upper()
    inputText = inputText.upper()
    for i in range(0, len(inputText)):
        indexInKey = i % len(key)
        possibleResultLetter = ord(inputText[i]) - ord(key[indexInKey]) + 65
        if possibleResultLetter < 64:
            possibleResultLetter += 26
        result += chr(possibleResultLetter)
    return result

def decryptFirstStage(toDecrypt):
    toDecrypt = toDecrypt.lower()
    print "original string:", toDecrypt[:10] + "...", "\t\tI.C. =", calculateIC(toDecrypt)
    for i in range(0, len(toDecrypt)):
        lengthOfKey = i + 1
        # assuming this is the length of the key, find the lists of letters
        # enciphered using the same cipher
        print lengthOfKey, "\t\t\t\t\t\t\tAverage I.C. = ",
        # create dictionary of each sequence generated by a key of this length
        averageIC = 0.0
        sequenceDictionary = {}
        for index in range(0, len(toDecrypt)):
            sequenceNumber = index % lengthOfKey
            if sequenceNumber in sequenceDictionary:
                sequenceDictionary[sequenceNumber] += toDecrypt[index]
            else:
                sequenceDictionary[sequenceNumber] = toDecrypt[index]

        hadZeroError = False
        for stringSequence in sequenceDictionary.values():
            try:
                averageIC += calculateIC(stringSequence)
            except ZeroDivisionError:
                hadZeroError = True
                break
        if hadZeroError == True:
            averageIC = 'N/A'
        else:
            averageIC /= len(sequenceDictionary.keys())
        print averageIC


def decryptSecondStage(inputText, keyLength):
    sequenceDictionary = {}
    for index in range(0, len(inputText)):
        sequenceNumber = index % keyLength
        if sequenceNumber in sequenceDictionary:
            sequenceDictionary[sequenceNumber] += inputText[index]
        else:
            sequenceDictionary[sequenceNumber] = inputText[index]

    #iterate through each sequence
    for index in sequenceDictionary.keys():
        print "Sequence number:", index
        stringSequence = sequenceDictionary[index]
        #rotate sequence all 26 times, find the lowest chi - square
        allRotations = rotateCaesarBackwards(stringSequence)
        rotationNumber = 0
        rotatedString = ""
        calculatedChiSquared = float("inf")

        for numRotations in allRotations.keys():
            currentString = allRotations[numRotations]
            currentChi = chiSquared(currentString)
            if currentChi < calculatedChiSquared:
                rotationNumber = numRotations
                rotatedString = currentString
                calculatedChiSquared = currentChi

        print rotationNumber, rotatedString, calculatedChiSquared, rotationNumberToCharacter(rotationNumber)



def calculateIC(inputText):
    inputText = "".join(inputText.lower().split())
    # maps characters to their frequencies
    frequency = getFrequencyOfText(inputText)
    ic = 0.0
    for letter in ascii_lowercase:
        if letter in frequency:
            ic += frequency[letter] * (frequency[letter] - 1)

    ic /= len(inputText) * (len(inputText) - 1)
    return ic


def rotateCaesarBackwards(inputText):
    inputText = "".join(inputText.lower().split())
    rotationDictionary = {}
    for i in range(0,26):
        resultAfterRotation = ""
        for letter in inputText:
            resultLetterOrdinal = ord(letter)-i
            if (resultLetterOrdinal < 97):
                resultLetterOrdinal += 26
            resultAfterRotation+=chr(resultLetterOrdinal)
        rotationDictionary[i] = resultAfterRotation
    return rotationDictionary


def chiSquared(inputText):
    inputText = "".join(inputText.lower().split())
    chiSquaredResult = 0.0
    textCount = getFrequencyOfText(inputText)
    for letter in ascii_lowercase:
        if letter in textCount:
            actualCount = textCount[letter]
        else:
            actualCount = 0
        expectedCount = englishExpectedFrequencies[letter] * len(inputText)
        chiSquaredResult += ((actualCount - expectedCount) ** 2) / expectedCount
    return chiSquaredResult


def getFrequencyOfText(inputText):
    frequency = {}
    for letter in inputText:
        if letter in frequency:
            frequency[letter] += 1
        else:
            frequency[letter] = 1
    return frequency

def rotationNumberToCharacter(number):
    return chr(number+97)


def decryptUsingQuadgramLocalSearch(inputText, keyLength):
    inputText = "".join(inputText.lower().split())
    key = initializeRandomKey(keyLength)
    print "INITIAL KEY: ", key
    ngram = ngram_score("english_quadgrams.txt")
    fitness = ngram.score(decrypt(inputText,key))
    print "INITIAL FITNESS: ", fitness
    improvement = True
    indexOfKeyToModify = 0
    while improvement == True:
        bestFitness = float("-inf")
        bestKey = ""
        childrenKeys = computeChildren(key,indexOfKeyToModify)
        indexOfKeyToModify = (indexOfKeyToModify + 1) % keyLength
        for childKey in childrenKeys:
            childScore = ngram.score(decrypt(inputText,childKey))
            if childScore > bestFitness:
                bestFitness = childScore
                bestKey = childKey
        if bestFitness <= fitness:
            improvement = False
        else:
            fitness = bestFitness
            key = bestKey
            print fitness, key
    print key


def computeChildren(keyString,indexToModify):
    children = []
    for letter in ascii_lowercase:
        child = list(keyString)
        child[indexToModify] = letter
        children.append("".join(child))
    return children

def initializeRandomKey(keyLength):
    toReturn = ""
    for i in range(keyLength):
        toReturn += chr(97+randint(0,25))
    return toReturn




if __name__ == "__main__":
    print encrypt('goodchocolatetastesgoodandbadchocholatetastesbad', 'zhao')
    # decryptFirstStage(
    #         'vptnvffuntshtarptymjwzirappljmhhqvsubwlzzygvtyitarptyiougxiuydtgzhhvvmumshwkzgstfmekvmpkswdgbilvjljmglmjfqwioiivknulvvfemioiemojtywdsajtwmtcgluysdsumfbieugmvalvxkjduetukatymvkqzhvqvgvptytjwwldyeevquhlulwpkt')
    # decryptSecondStage('vptnvffuntshtarptymjwzirappljmhhqvsubwlzzygvtyitarptyiougxiuydtgzhhvvmumshwkzgstfmekvmpkswdgbilvjljmglmjfqwioiivknulvvfemioiemojtywdsajtwmtcgluysdsumfbieugmvalvxkjduetukatymvkqzhvqvgvptytjwwldyeevquhlulwpkt',7)

    decryptFirstStage('FVORBOOQNSAHDAAGSLSUNVDOMKBOCJHCBOOZZAEHZZTSRIAR')
    decryptSecondStage('FVORBOOQNSAHDAAGSLSUNVDOMKBOCJHCBOOZZAEHZZTSRIAR',4)

    decryptUsingQuadgramLocalSearch('FVORBOOQNSAHDAAGSLSUNVDOMKBOCJHCBOOZZAEHZZTSRIAR',4)