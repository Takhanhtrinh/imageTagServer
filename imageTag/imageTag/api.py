import uuid
import hashlib
import boto3
import sched
import time
import datetime
import random
import json
import re


TABLE1 = 'user'
TABLE2 = 'user1'
TABLE3 = 'user2'
PHOTO_USER = 'userPhoto'
HASHTAG_TABLE = "hashtag"
HASHTAG_IMAGE = 'photoht'
REGISTER_FAILED_UNKNOW = -20
REIGSTER_PASSWORD_LENGTH_FAILED = -19
REGISTER_EXCESS_LENGTH = -18
REGISTER_EXIST = -17
REGISTER_OK = 1
GET_USER_NOT_FOUND = -16
LOGIN_FAILED_INVALID_USR = -15
LOGIN_FAILED_PW_NOT_MATCH = -14
LOGIN_OK = 2
GET_USER_FAILED = -13

DESCRIBE_TABLE_NOT_FOUND= -12
DESCRIBE_TABLE_ACTIVE = 3
DESCRIBE_TABLE_CRAETING = 4
DESCRIBE_TABLE_UPDATE = 5
# DESCRIBE_TABLE_

HASHTAG_NOT_EXIST = -11

CREATE_HASHTAG_ITEM_FAILED = -10
CREATE_HASHTAG_ITEM_SUCCESS = 6

UPLOAD_IMAGE_TO_BUCKET_FAILED = -9
UPDATE_PHOTO_COUNT_USER_FAILED = -8

UPLOAD_IMAGE_TO_BUCKET_SUCCESS = 7

PUT_PHOTO_USER_FAILED = -7
PUT_PHOTO_USER_SUCCESS = 8

PUT_PHOTO_HASHTAG_FAILED = -6
PUT_PHOTO_HASHTAG_SUCCESS = 9

GET_USER_PHOTO_FAILED = -5

GET_HASHTAG_PHOTO_FAILED = -5

UPLOAD_PHOTO_SUCCESS = 10
UPLOAD_PHOTO_FAILED = -4

SHARE_PHOTO_VIA_MSG_SUCCESS = 11
SHARE_PHOTO_VIA_MSG_FAILED = -3

ACCESS_KEY = ''
SECRET_KEY = ''

S3ACCESS_KEY = ''
S3SECRET_KEY = ''

BUCKET_NAME = 'photobucketp5'
BUCKET_LINK = 'https://s3-us-west-2.amazonaws.com/photobucketp5/'




def getClientBoto3():
    client = boto3.client('dynamodb', region_name='us-west-2',
                              aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
    return client

def register(usr, pw):
    userNameLen = len(usr)
    if (userNameLen > 24 and userNameLen > 4):
        return REGISTER_EXCESS_LENGTH
    passlen = len(pw)
    if (passlen < 8):
        return REIGSTER_PASSWORD_LENGTH_FAILED
    else:
        sum = 0
        for i in range(0, userNameLen):
            aChar = usr[i]
            value = ord(aChar)
            sum = sum + value
        # check to see if the userName exist in the database
        client = getClientBoto3()
        tableName = 'user'

        data = client.query(TableName=tableName, KeyConditionExpression='userName = :userName',
                            ExpressionAttributeValues={':userName': {'S': usr}})
        items = data['Items']
        numberOfUser = len(items)
            # no user with same name exist
        if (numberOfUser == 0):
            pw = pw.encode('utf8')
            hashed_password = hashlib.sha512(pw).hexdigest()
            key = {}
            key['userName'] = usr
            key['password'] = hashed_password
            try:
                client.put_item(Item={'userName': {'S': usr}, 'password': {
                                'S': hashed_password}, 'photoCount': {'N' : str(0)}}, TableName='user')
                return REGISTER_OK
            except Exception as e:
                print("register usr: " + usr + " failed")
                print(e)
                return REGISTER_FAILED_UNKNOW

        else:
            return REGISTER_EXIST
        print(items)
        # print(data)
        return data


def login(usr, pw):
    usrLen = len(usr)
    pwlen = len(pw)
    if(usrLen > 24):
        return LOGIN_FAILED_INVALID_USR
    if (pwlen < 8):
        return LOGIN_FAILED_PW_NOT_MATCH
    else:
        client = getClientBoto3()
        tableName = 'user'
        pw = pw.encode('utf8')
        hashed_password = hashlib.sha512(pw).hexdigest()
        data = client.query(TableName=tableName, KeyConditionExpression='userName = :userName',
                            ExpressionAttributeValues={':userName': {'S': usr}})
        # print(data)
        items = data['Items']
        itemLen = len(items)
        if (itemLen == 0):
            return LOGIN_FAILED_INVALID_USR
        else:
            user = items[0]
            passwordField = user['password']
            password = passwordField['S']
            print(user)
            if (password != hashed_password):
                return LOGIN_FAILED_PW_NOT_MATCH
            else:
                return LOGIN_OK



def getUser(usr):
    lenUser = len(usr) 
    if (lenUser > 24 and lenUser < 4) :
        return GET_USER_FAILED
    client = getClientBoto3()
    data = client.query(TableName=TABLE1, KeyConditionExpression='userName = :userName',
                        ExpressionAttributeValues={':userName': {'S': usr}})
    items = data['Items']
    if (len(items) == 0):
        return GET_USER_NOT_FOUND
    else:
        user = {}
        item = items[0]
        user['userName'] = item['userName']['S']
        user['password'] = item['password']['S']
        user['photoCount'] = item['photoCount']['N']
        return user

def updatePhotoCountUser(usr):
    user = getUser(usr)
    if (user == GET_USER_FAILED): 
        return GET_USER_FAILED
    elif (user == GET_USER_NOT_FOUND):
        return GET_USER_NOT_FOUND
    try:
        client = getClientBoto3()
        data = client.update_item(TableName = TABLE1, ReturnValues = "UPDATED_OLD" , Key = {'userName' : {'S' : usr}}, UpdateExpression = "set photoCount = photoCount + :val", ExpressionAttributeValues = {":val" : {'N': '1'}})
        #  return previous id 
        rt = data['Attributes']['photoCount']['N']
        return rt
    except Exception as e:
        print('update photo count user failed ')
        return UPDATE_PHOTO_COUNT_USER_FAILED

def putPhotoToUser(usr,fileName):
    index = updatePhotoCountUser(usr)
    if (index == UPDATE_PHOTO_COUNT_USER_FAILED):
        return index
    else:
        client = getClientBoto3()
        try:
            timestamp = int(time.time())
            client.put_item(TableName = PHOTO_USER, Item = {'userName' : {'S'
                : usr}, 'id' : {'N' : str(index)}, 'link': {'S' : BUCKET_LINK
                    +  fileName}, 'timeStamp' : {'N': str(timestamp)}})
            return PUT_PHOTO_USER_SUCCESS
        except Exception as e:
            print("put photo to user: " + usr + " failed")
            print(e)
            return PUT_PHOTO_USER_FAILED
        
def putPhotoToHashTag(usr,file,hashtag):
    user = getUser(usr) 
    if (user  == GET_USER_FAILED):
        return GET_USER_FAILED
    elif(user == GET_USER_NOT_FOUND):
        return GET_USER_NOT_FOUND
    index = updateHashTagCount(hashtag)
    # print('putting link to hashtag table usr:' + usr + ' hashtag: ' + hashtag + ' index: ' + index )
    if (index == HASHTAG_NOT_EXIST):
        flag = createHashTagItem(hashtag)
        if (flag == CREATE_HASHTAG_ITEM_FAILED):
            return CREATE_HASHTAG_ITEM_FAILED
        else:
            index = updateHashTagCount(hashtag)
    client = getClientBoto3()
    try:
        timestamp = int(time.time())
        client.put_item(TableName = HASHTAG_IMAGE, Item = {'tagName': {'S'
            : hashtag}, 'id' : {'N': str(index)}, 'link': {'S': BUCKET_LINK
                + file}, 'timeStamp': {'N': str(timestamp)}})
        return PUT_PHOTO_HASHTAG_SUCCESS
    except Exception as e:
        print("put photo hashtag failed user: " + usr  + ' hashtag ' + hashtag )
        print(e)
        return PUT_PHOTO_HASHTAG_FAILED


def createHashTagItem(tagName):
    client = getClientBoto3()
    try:
        client.put_item(TableName = HASHTAG_TABLE, Item = {'tagName' : {'S' : tagName}, 'photoCount': {'N': '0'}})
        return CREATE_HASHTAG_ITEM_SUCCESS
    except Exception as e :
        print("CreateHashTagItem Failed to create hashtag: " + tagName)
        return CREATE_HASHTAG_ITEM_FAILED


def updateHashTagCount(hashtag):
    client = getClientBoto3()
    data = client.query(TableName = HASHTAG_TABLE, KeyConditionExpression = 'tagName = :tagName',ExpressionAttributeValues = {':tagName': {'S': hashtag}})
    if (data['Count'] == 0):
        return HASHTAG_NOT_EXIST
    else:
        data = client.update_item(TableName = HASHTAG_TABLE, ReturnValues = "UPDATED_OLD" , Key = {'tagName' : {'S' : hashtag}}, UpdateExpression = "set photoCount = photoCount + :val", ExpressionAttributeValues = {":val" : {'N': '1'}})
        #  return previous id 
        rt = data['Attributes']['photoCount']['N']
        return rt


def uploadImageToBucket(usr,image): 
    clientS3 = boto3.client('s3', aws_access_key_id = S3ACCESS_KEY, aws_secret_access_key = S3SECRET_KEY)
    timeStamp = int(time.time())
    salt = random.random()
    key = str(timeStamp) + str(salt) + usr
    key = key.encode('utf8')
    hashedKey = hashlib.sha512(key).hexdigest()
    try:
        clientS3.put_object(Bucket = BUCKET_NAME, Key = hashedKey, ACL = 'public-read', Body = image)
        return hashedKey
    except Exception as e: 
        print("clients3 upload photo to s3 failed")
        print(e)
        return UPLOAD_IMAGE_TO_BUCKET_FAILED

def userUploadPhoto(usr, image):
    user = getUser(usr)
    if (user == GET_USER_FAILED):
        return GET_USER_FAILED
    elif (user == GET_USER_NOT_FOUND):
        return GET_USER_NOT_FOUND
    flag = uploadImageToBucket(usr,image)
    if (flag != UPLOAD_IMAGE_TO_BUCKET_FAILED):
        flag =  putPhotoToUser(usr, flag)
        return flag
    else:
        return flag

def userUploadHashTag(usr, hashtag, image):
    lenht = len(hashtag)
    if (lenht == 0):
        flag = userUploadPhoto(usr, image)
        if (flag != UPLOAD_IMAGE_TO_BUCKET_FAILED):
            return UPLOAD_PHOTO_SUCCESS
    else:
        hashKeyed = uploadImageToBucket(usr,image)
        if (hashKeyed != UPLOAD_IMAGE_TO_BUCKET_FAILED):
            print('upload image to bucket success')
            flag = putPhotoToUser(usr, hashKeyed)
            print('put photo to user: ' + str(flag))
            if (flag == PUT_PHOTO_USER_SUCCESS):
                flag = putPhotoToHashTag(usr,hashKeyed,hashtag)
                print('put photo to hashtag: ' + str(flag))
                return UPLOAD_PHOTO_SUCCESS
            return UPLOAD_PHOTO_FAILED
        return UPLOAD_PHOTO_SUCCESS

def userGetImage(usr, fromId, toId, limit = 10):
    user = getUser(usr)
    if (user == GET_USER_NOT_FOUND):
        return GET_USER_NOT_FOUND 
    elif(user == GET_USER_NOT_FOUND) :
        return GET_USER_FAILED 
   
    try:
         client = boto3.client('dynamodb', region_name='us-west-2',
                                 aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
         numberOfItem =  user['photoCount']  
         data = {}
         data['items'] = []
         if (numberOfItem == 0):
             return data
         else:
            response = client.query(TableName = PHOTO_USER, KeyConditionExpression
                    = 'userName = :usr AND id BETWEEN  :fromId AND :toId',
                    ExpressionAttributeValues = {':usr': {'S' : usr}, ':fromId'
                        : {'N' : str(fromId)}, ':toId' : {'N' : str(toId)}}, Limit
                        = limit )
            print(response)
            numberOfItem = response['Count']
            numberOfItem = int(numberOfItem)
            data['count'] = numberOfItem
            items = response['Items']
            for i in range(0, numberOfItem):
               userName = items[i]['userName']['S']
               print('userName: ' + userName)
               print('usr: ' + usr)
               if (userName == usr):
                    picId = items[i]['id']['N']
                    link = items[i]['link']['S']
                    timestamp = items[i]['timeStamp']['N']
                    jsonData = {'id' : picId, 'link': link, 'timeStamp' : timestamp}
                    data['items'].append(jsonData)
            return data
    except Exception as e:
        print("USER GET IMAGE FAILED")
        print(e)
        return GET_USER_PHOTO_FAILED


def userGetHashTagImages(hashtag, fromId, toId, limit = 10 ):
    try:
        client = getClientBoto3()
        data = client.query(TableName = HASHTAG_IMAGE, KeyConditionExpression
                    = 'tagName = :tag AND id BETWEEN :v1 AND :v2',
                    ExpressionAttributeValues = {':tag': {'S' : hashtag}, ':v1'
                        : {'N': str(fromId)}, ':v2' : {'N': str(toId)}}, Limit
                    = limit)
        print(data)
        numberOfItem = data['Count']
        print("numbre of item: " + str(numberOfItem))
        jsonData = {}
        jsonData['items'] = []
        if (numberOfItem == 0):
            return jsonData
        else:
            items = data['Items']
            for i in range(0, numberOfItem):
                item = items[i] 
                tagName = item['tagName']['S']
                link = item['link']['S']
                idn = item['id']['N']
                timeStamp = item['timeStamp']['N']
                rtjson = {'tagName' : tagName, 'link': link, 'id': int(idn),
                        'timeStamp': int(timeStamp)} 
                jsonData['items'].append(rtjson)
        
        return jsonData
    except Exception as e:
        print('USER GET HASHTAG IMAGE FAILED')
        print(e)
        return GET_HASHTAG_PHOTO_FAILED

def filterForScan(data, keyWord):
    numberOfItem = data['Count']
    items = data['Items']
    rt = {}
    rt['items'] = []
    for i in range(0, numberOfItem):
        item = items[i]
        tagName = item[keyWord]['S']
        rt['items'].append(tagName)
    return rt


    #use to search user and hashtag
def scanData(tableName, attribute, value):
    client = getClientBoto3()
    response =client.scan(TableName = tableName, FilterExpression
            = 'begins_with(' + attribute +  ',:val)',
            ExpressionAttributeValues = {':val': {'S': value}} )
    return response

def searchHashTag(hashTag):
    data = scanData(HASHTAG_TABLE, 'tagName', hashTag)
    return filterForScan(data,'tagName')

def searchUser(userName):
    data = scanData(TABLE1, 'userName', userName)
    return filterForScan(data,'userName')

def sendLinkViaPhone(phoneNumber, userName, link):
    data = getUser(userName)
    if (data == GET_USER_NOT_FOUND):
        return SHARE_PHOTO_VIA_MSG_FAILED
    client = boto3.client('sns', aws_access_key_id = ACCESS_KEY,
            aws_secret_access_key = SECRET_KEY,region_name = 'us-west-2')
    try:
        phone = '+1' + str(phoneNumber)
        match = re.search('\/(\w+)$', link)
        if re:
            newUrl = 'https://s3-us-west-2.amazonaws.com/p5showimage/imageLoad.html?data='
            link = match.group(1) 
            link = newUrl + link
        message = 'Message from ImageTag. ' + userName + ' wants to share with you an image: ' + link
        response = client.publish(Message = message,PhoneNumber = phone
                )
        print(response)
        return SHARE_PHOTO_VIA_MSG_SUCCESS
    except Exception as e: 
        print('share image via msg failed') 
        print(e) 
        return SHARE_PHOTO_VIA_MSG_FAILED



#print(userGetHashTagImages('grade1234',1,1))
#print(userGetImage('trinhta2',0,10))
# print(register('LeoLe3','nguvklhaha'))
# print(login('LeoLe3', 'nguvklhaha'))
# print(getUser('trinh'))
# print(register('trinhta2', "dumbass123"))
# createUserPhotoTable('trinhta')
# print(createPhotoHashTag('vkl'))
# uploadPhoto('trinhta2','thisHashTabIsCool', 'photo ne')
# appendImageUrlToNOSQL('trinhta2')
# uploadImageToBucket('temp', 'trinhta')
#file = open('/Users/trinhta/Desktop/test.png','rb')
#buffer = file.read()
#print(userUploadHashTag('trinhta2','grade1234', buffer))
# print(putPhotoToUser('trinhta2','alasjdflaskjdflaskjf'))
# print(buffer)
# print(userUploadHashTag('trinhta2','thisIsNoCool',buffer))
# uploadPhoto('trinhta2','myphoto',buffer)
# print(register('john123','example123'))
# print(getPhotoWithUser('trinhta2', 0,8,10))
# print(putPhotoToHashTag('trinhta2','alkdsjfladsjf','thisiscool'))
#data = scanData(TABLE1, 'userName', 'trinh')
#print(filterForScan(data,'userName'))
