import json

with open('outputPoems-2.txt', 'r') as outfile:
    poems = outfile.read()

with open('cmu_dict.json', 'r') as json_file:
    cmu = json.load(json_file)

def countSyllablesInWord(word):
    try:
        syllables = cmu[word]
    except KeyError:
        syllables = 1
    return syllables

def countSyllablesInText(inputText):
    inputText = inputText.split('\n')
    inputText = [x for x in inputText if x]
    #print(inputText)
    return [sum([countSyllablesInWord(word.upper()) for word in line.split(' ') if word]) for line in inputText]

#print(''.join(poems))
poems = [x for x in poems.split('<|endoftext|>') if x]
print(len(poems))
poems = [poem for poem in poems if sum(countSyllablesInText(poem)) == 17]

with open("outputPoems2.json", 'w') as outfile:
    outfile.write(json.dumps(poems))