import json
import base64
import os
import urllib.request
from urllib.error import HTTPError
from time import sleep


def find_all_images(files_path):
    images = []
    for root, dirs, files in os.walk(files_path):
        for file in files:
            if file.endswith(".jpg"):
                file_path = os.path.join(root, file).replace(files_path, "")
                images.append(file_path)
    return images


def generate_vision_api_json(filename):
    requests_json_object = {}
    request_array = []
    file = open(filename, "rb")
    image_json_object = {'features': [{"type": "TEXT_DETECTION", "maxResults": 10},
                                      {"type": "SAFE_SEARCH_DETECTION", "maxResults": 10}],
                         'image': {'content': base64.b64encode(file.read()).decode('utf-8')}}
    file.close()
    request_array.append(image_json_object)
    requests_json_object['requests'] = request_array
    return requests_json_object


def process_google_vision_api(file_request_json):
    json_data = json.dumps(file_request_json).encode('utf-8')
    req = urllib.request.Request(
        url='https://vision.googleapis.com/v1alpha1/images:annotate?key=')
    req.add_header('Content-Type', 'application/json')
    response = urllib.request.urlopen(req, json_data)
    return json.loads(response.read().decode("utf-8"))['responses'][0]


if __name__ == "__main__":
    data_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data//")
    print(data_path)
    images_to_process = find_all_images(data_path)
    html_table = '<html><body><table border="1"><td><b>Image</b></td><td width="300"><b>Path</b></td>' \
                 '<td width="250"><b>Safe search results</b></td><td><b>Text search results</b></td>'
    for i, image_path in enumerate(images_to_process):
        request_json = generate_vision_api_json(os.path.join(data_path, image_path))
        answer_json = {}
        safeText = ''
        ocrText = ''
        while True:
            try:
                print('Sending image number {}, url "{}"'.format(i, image_path))
                answer_json = process_google_vision_api(request_json)
                break
            except HTTPError as err:
                safeText = 'Error processing Google Vision API request: ' + err.reason
                print(safeText)
                print('Retrying in 1 second...')
                sleep(1)
        if 'safeSearchAnnotation' in answer_json:
            safeText = 'Adult: {}<br>Violence: {}<br>' \
                       'Medical: {}<br>Spoof: {}<br>'.format(answer_json['safeSearchAnnotation']['adult'],
                                                             answer_json['safeSearchAnnotation']['violence'],
                                                             answer_json['safeSearchAnnotation']['medical'],
                                                             answer_json['safeSearchAnnotation']['spoof'])
            print('Safe search:', answer_json['safeSearchAnnotation'])
        if 'textAnnotations' in answer_json:
            ocrText = json.dumps(answer_json['textAnnotations']).encode('utf-8')
            print('Text search:', answer_json['textAnnotations'])
        html_table += '<tr><td><a href="{}"><img src="file:///{}" width="300px" /></a>' \
                      '</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(os.path.join(data_path, image_path),
                                                                           os.path.join(data_path, image_path),
                                                                           image_path,
                                                                           safeText,
                                                                           ocrText)
        final_html = html_table + '</table></body></html>'
        html_file = open('.//results.html', "w")
        html_file.write(html_table)
        html_file.close()
