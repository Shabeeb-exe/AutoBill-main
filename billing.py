#!/usr/bin/env python

import cv2
import os
import sys, getopt
import signal
import time
from edge_impulse_linux.image import ImageImpulseRunner

import RPi.GPIO as GPIO 
from hx711 import HX711


import requests
import json
from requests.structures import CaseInsensitiveDict

runner = None
show_camera = True


hx = HX711(5, 18)
hx.set_reading_format("MSB", "MSB")
referenceUnit = 108
hx.set_reference_unit(referenceUnit)
hx.reset()
hx.tare()

flag = 0

id_product = 1
list_label = []
list_weight = []
count = 0
final_weight = 0
taken = 1

a = 'Tomato'
b = 'Brush'
l = 'Lays'
c = 'Tata salt'

def now():
    return round(time.time() * 1000)

def get_webcams():
    port_ids = []
    for port in range(5):
        print("Looking for a camera in port %s:" %port)
        camera = cv2.VideoCapture(port)
        if camera.isOpened():
            ret = camera.read()[0]
            if ret:
                backendName =camera.getBackendName()
                w = camera.get(3)
                h = camera.get(4)
                print("Camera %s (%s x %s) found in port %s " %(backendName,h,w, port))
                port_ids.append(port)
            camera.release()
    return port_ids

def sigint_handler(sig, frame):
    print('Interrupted')
    if (runner):
        runner.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, sigint_handler)

def help():
    print('python classify.py <path_to_model.eim> <Camera port ID, only required when more than 1 camera is present>')

def find_weight():
    global c_value
    global hx
    try:
        weight = max(0,int(hx.get_weight(5)))
        #round(weight,1)
        print(weight, 'g')
        return weight
    except (KeyboardInterrupt, SystemExit):
        print('Bye :)')
               
def post(label,price,weight, final_rate,take):
    global id_product
    global list_label
    global list_weight 
    global count
    global final_weight
    global taken
    url = "https://autobill-main-8knj.onrender.com/product"
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"
    data_dict = {"id":id_product,"name":label,"price":price,"units":"units","taken":1,"weight":weight,  "payable":final_rate}
    data = json.dumps(data_dict)
    resp = requests.post(url, headers=headers, data=data)
    print(resp.status_code)
    id_product = id_product + 1  
    time.sleep(3)
    list_label = []
    list_weight = []
    count = 0
    final_weight = 0
    taken = 1
                
def list_com(label,final_weight):
    global count
    global taken
    if final_weight > 2 :	
       list_weight.append(final_weight)
    #    if count > 1 and list_weight[-1]  >list_weight[-2]:
    #        taken = taken + 1
    #    taken = taken + 1
    list_label.append(label)
    print("New Item detected")
    print("Final weight is",final_weight)
    rate(final_weight,label,1)   
    print("Place next item...")       
    time.sleep(5)
	
def rate(final_weight,label,taken):
    print("Calculating rate")
    if label == a :
         print("Calculating rate of",label)
         final_rate_a = final_weight * 0.001  
         price = 40     
         post(label,price,final_weight, final_rate_a * price,taken)
    elif label == b :
         print("Calculating rate of",label)
         price = 20
         final_rate_b = price * taken
         post(label,price,final_weight,final_rate_b,taken)
    elif label == l:
         print("Calculating rate of",label)
         price = 10
         final_rate_l = price * taken
         post(label,price,final_weight,final_rate_l,taken)
    else :
         print("Calculating rate of",label)
         final_rate_c = final_weight * 0.001  
         price = 25     
         post(label,price,final_weight, final_rate_c * price,taken)

def main(argv):
    global flag
    global final_weight
    if flag == 0 :
        find_weight()
        flag = 1      
    try:
        opts, args = getopt.getopt(argv, "h", ["--help"])
    except getopt.GetoptError:
        help()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            help()
            sys.exit()

    if len(args) == 0:
        help()
        sys.exit(2)

    model = args[0]

    dir_path = os.path.dirname(os.path.realpath(__file__))
    modelfile = os.path.join(dir_path, model)

    print('MODEL: ' + modelfile)

    with ImageImpulseRunner(modelfile) as runner:
        try:
            model_info = runner.init()
            print('Loaded runner for "' + model_info['project']['owner'] + ' / ' + model_info['project']['name'] + '"')
            labels = model_info['model_parameters']['labels']
            if len(args)>= 2:
                videoCaptureDeviceId = int(args[1])
            else:
                port_ids = get_webcams()
                if len(port_ids) == 0:
                    raise Exception('Cannot find any webcams')
                if len(args)<= 1 and len(port_ids)> 1:
                    raise Exception("Multiple cameras found. Add the camera port ID as a second argument to use to this script")
                videoCaptureDeviceId = int(port_ids[0])

            camera = cv2.VideoCapture(videoCaptureDeviceId)
            ret = camera.read()[0]
            if ret:
                backendName = camera.getBackendName()
                w = camera.get(3)
                h = camera.get(4)
                print("Camera %s (%s x %s) in port %s selected." %(backendName,h,w, videoCaptureDeviceId))
                camera.release()
            else:
                raise Exception("Couldn't initialize selected camera.")

            next_frame = 0 # limit to ~10 fps here

            for res, img in runner.classifier(videoCaptureDeviceId):
                if (next_frame > now()):
                    time.sleep((next_frame - now()) / 1000)

                # print('classification runner response', res)

                if "bounding_boxes" in res["result"].keys():
                    if len(res["result"]['bounding_boxes']) == 0:
                        continue
                    bbox = max(res['result']['bounding_boxes'], key=lambda x:x['value'])
                    score = bbox['value']
                    label = bbox['label']        
                    if score > 0.9 :
                        final_weight = find_weight()
                        list_com(label,final_weight)
                        if label == a:
                            print('Tomato detected')       
                        elif label == b:
                            print('Brush detected')
                        elif label == l:
                            print('Lays deteccted')
                        elif label == c:
                            print('Tata salt detected')
                    print('Result (%d ms.) ' % (res['timing']['dsp'] + res['timing']['classification']), end='')
                    print('', flush=True)
                next_frame = now() + 100
        finally:
            if (runner):
                runner.stop()

if __name__ == "__main__":
    main(sys.argv[1:])
