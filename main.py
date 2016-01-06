import sys, getopt
import json
import collections
import base64
import os
import urllib.request


def main(argv):
    inputfilename = ''
    outputfilename = ''
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ifile=", "ofile="])
    except getopt.GetoptError:
        print('generatejson.py -i  -o ')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('generatejson.py -i  -o ')
            print('Input File format:')
            print('FileURI Feature:maxResults ...')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfilename = arg
        elif opt in ("-o", "--ofile"):
            outputfilename = arg

    inputFile = open(inputfilename, 'r')
    lineCount = 0
    requestsJsonObj = {}
    requestArray = []
    for inputLine in inputFile:
        lineCount = lineCount + 1
        print(inputLine)
        wordCount = 0
        contentJsonObj = {}
        imageJsonObj = {}
        featureJsonObj = []
        lineWords = inputLine.split(" ")
        if len(lineWords) < 2:
            print("Invalid input file format")
            print("Valid Format: FileURI feature:maxResults feature:maxResults ....")
            sys.exit()
        for word in lineWords:
            if wordCount == 0:
                imageFile = open(word, 'rb')
                contentJsonObj['content'] = base64.b64encode(imageFile.read()).decode('utf-8')
                # print("img:" + word)
            else:
                detectValues = word.split(":")
                valueCount = 0
                featureDict = collections.OrderedDict()
                for values in detectValues:
                    if valueCount == 0:
                        detectionType = getDetectionType(values)
                        featureDict['type'] = detectionType
                        print("detect:" + detectionType)
                    else:
                        maxResults = values.rstrip()
                        featureDict['maxResults'] = maxResults
                        print("results: " + maxResults)
                    valueCount = valueCount + 1
                featureJsonObj.append(featureDict)
            wordCount = wordCount + 1
        imageJsonObj['features'] = featureJsonObj
        imageJsonObj['image'] = contentJsonObj
        requestArray.append(imageJsonObj)
    requestsJsonObj['requests'] = requestArray
    with open(outputfilename, 'w') as outfile:
        json.dump(requestsJsonObj, outfile)


def getDetectionType(detectNum):
    if detectNum == "1":
        return "FACE_DETECTION"
    elif detectNum == "2":
        return "LANDMARK_DETECTION"
    elif detectNum == "3":
        return "LOGO_DETECTION"
    elif detectNum == "4":
        return "LABEL_DETECTION"
    elif detectNum == "5":
        return "TEXT_DETECTION"
    elif detectNum == "6":
        return "SAFE_SEARCH_DETECTION"
    return "TYPE_UNSPECIFIED"


def find_all_images(data_path):
    images = []
    for root, dirs, files in os.walk(data_path):
        for file in files:
            if file.endswith(".jpg"):
                file_path = os.path.join(root, file).replace(data_path, "")
                images.append(file_path)
    return images

def generate_vision_api_json(filename):
    requestsJsonObj = {}
    requestArray = []
    imageJsonObj = {}
    featureJsonObj = []
    featureDict = collections.OrderedDict()
    featureDict['type'] = "TEXT_DETECTION"
    featureDict['maxResults'] = 10
    featureJsonObj.append(featureDict)
    featureDict['type'] = "SAFE_SEARCH_DETECTION"
    featureDict['maxResults'] = 10
    featureJsonObj.append(featureDict)
    imageJsonObj['features'] = featureJsonObj
    file = open(filename, "rb")
    imageJsonObj['image'] = base64.b64encode(file.read()).decode('utf-8')
    file.close()
    requestArray.append(imageJsonObj)
    requestsJsonObj['requests'] = requestArray
    return requestsJsonObj


if __name__ == "__main__":
    data_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data//")
    print(data_path)
    images_to_process = find_all_images(data_path)
    for i, image_path in enumerate(images_to_process):
        print(i, image_path)
        request_json = generate_vision_api_json(os.path.join(data_path, image_path))
        with open(".//google-vision-api.json", 'w') as outfile:
            json.dump(request_json, outfile)
        json_data = open(".//google-vision-api.json", 'rb').read()
        #json_data = json.dumps(request_json)
        req = urllib.request.Request(url='https://vision.googleapis.com/v1alpha1/images:annotate?key=<key>')
        req.add_header('Content-Type', 'application/json')
        response = urllib.request.urlopen(req, json_data)
        print(response.text)
    # main(sys.argv[1:])
