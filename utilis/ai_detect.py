import requests
import os

def login(email = os.environ['GMAIL'] , key = os.environ['COPYLEAKS_API_KEY']):
  url = 'https://id.copyleaks.com/v3/account/login/api'


  payload = {
      'email':email,
      'key':key
  }
  header = {
      'Content-Type': 'application/json'

  }

  response = requests.post(url , json = payload , headers = header)
  return response.json()

def ai_detection(text , email = None , key = None):
  token = ''
  if email == None:
    response1 = login()
    token = response1['access_token']
  else:
    response1 = login(email , key)
    token = response1['access_token']



  
  url = 'https://api.copyleaks.com/v2/writer-detector/my-first-scan/check'
  headers = {
      'Content-Type': 'application/json',
      'Authorization': f'Bearer {token}'
  }

  payload = {
  "text": f'{text}',
  "sandbox": 'false'
  }

  response = requests.post(url , json = payload , headers = headers)
  print(response.json())
  return response.json()['summary']['ai']*100