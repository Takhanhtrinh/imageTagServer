from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import HttpResponse
from . import api 
import json
# Create your views here.

def home(request):
    return HttpResponse('This is web api for ImageTag')
@csrf_exempt 
def register(request):
    if (request.method == 'POST'):
        data = request.body 
        data = json.loads(data)
        usr = data['userName']
        psw = data['password']
        print('userName: ' + usr)
        print('psw: ' + psw)
        flag = api.register(usr,psw)
        rt = {}
        if (flag == api.REGISTER_EXCESS_LENGTH):
            rt['status'] = False
            rt['msg'] = 'User name should be between 4 and 24 characters'
        elif(flag == api.REGISTER_EXIST):
            rt['status'] = False
            rt['msg'] = 'This user name is already taken, please choose different name'
        elif(flag == api.REGISTER_FAILED_UNKNOW):
            rt['status'] = False
            rt['msg'] = 'Server side error'
        elif (flag == api.REGISTER_OK):
            rt['status'] = True
        rt = json.dumps(rt)
        return HttpResponse(rt)
@csrf_exempt
def login(request):
    if (request.method == 'POST'):
        data = request.body
        data = json.loads(data)
        usr = data['userName']
        psw = data['password']
        flag = api.login(usr,psw)
        rt = {}
        if (flag == api.LOGIN_FAILED_INVALID_USR):
            rt['status'] = False
            rt['msg'] = 'Invalid username' 
        elif(flag == api.LOGIN_FAILED_PW_NOT_MATCH):
            rt['status'] = False
            rt['msg'] = 'Please check your password'
        else:
            rt['status'] = True
        rt = json.dumps(rt)
        return HttpResponse(rt)
def searchUser(request,userName):
    if (request.method == 'GET'):
        rt = api.searchUser(userName)
        rt = json.dumps(rt)
        return HttpResponse(rt)

def searchHashTag(request,hashTag):
    if (request.method == 'GET'):
        rt = api.searchHashTag(hashTag)
        rt = json.dumps(rt)
        return HttpResponse(rt)
def getUserImage(request, userName,idn):
    if(request.method == 'GET'):
        idn = int(idn)
        flag = api.userGetImage(userName,idn,idn+10,10)
        rt = {}
        rt['items'] = []
        if (flag == api.GET_USER_NOT_FOUND):
            print('getUserImage: cant find userName: ' + userName)
            rt = json.dumps(rt)
        elif(flag == api.GET_USER_FAILED):
            print('getUserIamge: get user fail: ' + userName)
            rt = json.dumps(rt)
        elif(flag == api.GET_USER_PHOTO_FAILED):
            print('getUserImage: get user photo failed: ' + userName)
            rt = json.dumps(rt)
        else:
            rt = json.dumps(flag)
    return HttpResponse(rt)
def getHashTag(request, hashTag, idn):
    if (request.method == 'GET'):
        idn = int(idn)
        flag = api.userGetHashTagImages(hashTag, idn, idn + 10, 10)
        rt = {}
        rt['items'] = []
        if (flag == api.GET_HASHTAG_PHOTO_FAILED):
            rt = json.dumps(rt)
        else:
            rt = json.dumps(flag)
        return HttpResponse(rt)
        
@csrf_exempt
def upload(request):
    if (request.method == 'POST'):
        data = request.FILES['fileToUpload']
        usrName = request.POST['userName']
        hashTag = request.POST['hashTag']
        flag = api.userUploadHashTag(usrName,hashTag, data)
        rt = {}
        rt['status'] = False
        if (flag == api.UPLOAD_PHOTO_SUCCESS):
            rt['status'] = True
        else:
            rt['status'] = False
        rt = json.dumps(rt)

    return HttpResponse(rt)

@csrf_exempt 
def shareImageViaPhone(request):
    if (request.method == 'POST'):
        data = request.body 
        data = json.loads(data)
        phone = data['phone']
        link = data['link']
        userName = data['userName']
        flag = api.sendLinkViaPhone(phone,userName,link)
        rt = {}
        if (flag == api.SHARE_PHOTO_VIA_MSG_FAILED):
            rt['status'] = False 
            rt['msg'] = 'There is an error while sending the msg, please try again'
        else:
            rt['status']= True

        rt = json.dumps(rt)
        return HttpResponse(rt)

        
    
