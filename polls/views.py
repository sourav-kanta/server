#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import base64
import time
import os,json
import numpy
from scipy.misc import imread
from django.conf import settings
from PIL import Image

vidhan_soudha_speech="The Vidhana Soudha located in Bengaluru, is the seat of the state legislature of Karnataka.[1] It is an imposing building, constructed in a style sometimes described as Mysore Neo-Dravidian, and incorporates elements of Indo-Saracenic and Dravidian styles. The construction was completed in 1956.The Vidhana Soudha has four floors above and one floor below ground level and sprawls across an area of 2,300 by 1,150 feet (700 m × 350 m). It is the largest Legislative building in India. Its eastern face has a porch with 12 granite columns, 40 feet (12 m) feet tall. Leading to the foyer is a flight of stairs with 45 steps, more than 200 feet (61 m) wide. The central dome, 60 feet (18 m) in diameter, is crowned by a likeness of the Indian national emblem."
taj_mahal_speech="The Taj Mahal ( meaning Crown of the Palace) is an ivory-white marble mausoleum on the south bank of the Yamuna river in the Indian city of Agra. It was commissioned in 1632 by the Mughal emperor, Shah Jahan (reigned 1628–1658), to house the tomb of his favourite wife, Mumtaz Mahal. The tomb is the centrepiece of a 17-hectare (42-acre) complex, which includes a mosque and a guest house, and is set in formal gardens bounded on three sides by a crenellated wall.Construction of the mausoleum was essentially completed in 1643 but work continued on other phases of the project for another 10 years. The Taj Mahal complex is believed to have been completed in its entirety in 1653 at a cost estimated at the time to be around 32 million rupees, which in 2015 would be approximately 52.8 billion rupees (US$827 million). The construction project employed some 20,000 artisans under the guidance of a board of architects led by the court architect to the emperor, Ustad Ahmad Lahauri."
vidhan_soudha_img="https://upload.wikimedia.org/wikipedia/commons/thumb/2/25/Vidhana_Soudha_2012.jpg/300px-Vidhana_Soudha_2012.jpg"
taj_mahal_img="https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Taj_Mahal_Exterior.jpg/250px-Taj_Mahal_Exterior.jpg"

success_json={}
error_json={}

model=settings.MODEL 

def process_file(path):
    img=imread(path)
    np_img=numpy.asarray(img).astype('float32')/255.0    
    #print np_img.shape
    return np_img

def resize_image(path,item,dimX=None,dimY=None):
    if not dimX:
        dimX=64
    if not dimY:
        dimY=64
    im=Image.open(os.path.join(path,item))
    imResize = im.resize((dimX,dimY), Image.ANTIALIAS)
    imResize.save(os.path.join(path,item), 'JPEG', quality=90)


@csrf_exempt
def index(request):
    if not request.method=="POST":
        return HttpResponse("This is the api gateway for the application")
    try:        
    	image_base64=request.POST['image'];
    	f_name=str(int(time.time()*100))+".jpg"
    	#print f_name
    	#return HttpResponse(image_base64)
    	if not os.path.exists("media/uploads"):
    		os.makedirs("media/uploads");
    	with open("media/uploads/"+f_name, "wb") as fh:
    		fh.write(base64.decodestring(str(image_base64)))
    		fh.close()
        resize_image("media/uploads/",f_name);
        
        # Process Test Data

        test_img=process_file("media/uploads/"+f_name);
        print "Predicting"
        res=model.predict(numpy.stack([test_img]))
        print res
        numpy.set_printoptions(suppress=True)
        if res[0][1]>=res[0][0]:
            output="Vidhan Soudha"
            success_json['speech']=vidhan_soudha_speech
            success_json['img']=vidhan_soudha_img
        else:
            output="Taj Mahal"
            success_json['speech']=taj_mahal_speech
            success_json['img']=taj_mahal_img
        success_json['output']=output
        success_json['status']=1

        print f_name," has a prediction of : ",output," with ",res[0]
        return HttpResponse(json.dumps(success_json), content_type="application/json")
    except Exception,e:
    	print str(e)
        error_json['status']=-1
    	return HttpResponse(json.dumps(error_json), content_type="application/json");