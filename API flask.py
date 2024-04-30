#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@authors:
    Team 8 - Section A - MiBA
        Amos Wolf
        Yunfei Sun
        Lennard Riede
        Pere Gestí
        Nino Peranidze
        Nicolas Engelen
"""

# Import necessary libraries and modules
import datetime
from flask import Flask, request
from flask_restful import Resource, Api, reqparse
import jwt  # Import from PyJWT for handling JSON Web Tokens
import pandas as pd
import hashlib
import requests
import math

# Create a Flask application
app = Flask(__name__)
api = Api(app)

# Read existing user data from the CSV file
users_data = pd.read_csv('users.csv')  # Load user data from a CSV file
users_data['password'] = users_data['password'].astype(str)  # Ensure password data is treated as strings
secret_key = 'your secret key'  # Secret key for JWT encryption, could be changed with any string

# Define a resource for handling user login
class LogIn(Resource):
    def get(self):
        
        # Create a parser to handle request arguments
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, help='Email is required', required=True) # Email as mandatory argument
        parser.add_argument('password', type=str, help='Password is required', required=True) # Password as mandatory argument
        args = parser.parse_args()  # Parse arguments from the request

        # Check if the provided email exists in the database
        user_entry = users_data[users_data['email'] == args['email']]
        if user_entry.empty:
            return {'status': 401, 'response': 'Unauthorized - Invalid email'}, 401

        # Extract the stored password from the user_entry (a DataFrame) and compare
        stored_password = user_entry['password'].iloc[0]
        if stored_password != args['password']:
            return {'status': 401, 'response': 'Unauthorized - Invalid password'}, 401

        # Create an access token with the user's index as the identifier and expires in 1 hour
        user_index = user_entry.index[0]
        expiration_time = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        
        # Generate a JWT token using jwt.encode() method from PyJWT
        # The token will contain the user's index, expiration time, and scope Get, Post, Put, Delete (Delete the word to limit the scope)
        access_token = jwt.encode({'user_id': int(user_index), 'exp': expiration_time, 'scope': 'GetPostPutDelete'}, secret_key, algorithm='HS256')

        return {'status': 200, 'response': 'Successfully signed up', 'access_token': access_token}, 200

# Define a resource for managing characters
class Characters(Resource):
    def test_login(self, token):

        try:
            # Decode the JWT token
            print('testing')
            decoded_token = jwt.decode(token, secret_key, algorithms=['HS256'])
            
            # Extract and print the payload data
            user_index = decoded_token['user_id']
            expiration_time = decoded_token['exp']
            scope = decoded_token['scope']

            print(f"User ID: {user_index}")
            print(f"Expiration Time: {expiration_time}")
            return False, scope
        
        # Identify and return error types with status code and messages
        except jwt.ExpiredSignatureError:
            print("Token has expired")
            return {'status': 405, 'response': 'Token has expired'}, 405
        except jwt.DecodeError:
            print('Decode error')
            return {'status': 406, 'response': 'Failed to decode token (invalid signature or token)'}, 406
        except:
            print("Invalid token")
            return {'status': 407, 'response': 'Invalid token'}, 407

    def get(self):
        
        # Get the access token from the request
        token = request.args.get('access_token')
        print(token)
        # Check if the token is valid
        check=self.test_login(token)
        if check[0]:
            return check
        print(check[1])
        # Check if for this user the scope GET is allowed
        if 'get' in check[1].lower(): 
            print('get passed')
        else:
            return {'status': 408, 'response': 'Unauthorized - Invalid scope'}, 408
        
        print('test passed')
        data = pd.read_csv('data.csv')  # Read data from a CSV file
        # When reading from the CSV file, the characters IDs will be integers

        # Get character IDs and names from the request
        character_ids_param = request.args.get('Character IDs')
        character_names_param = request.args.get('Character Names')

        # Check either Character name or ID is provided in the request, but not both
        if character_names_param and character_ids_param:
            return {'status': 407, 'response': 'Provide either the Character Names or IDs, but not both.'}, 407
        
        # If receives Character ID
        if character_ids_param:
            try:
                print(character_ids_param)  # Print the received character IDs (for debugging)
                character_ids = list(map(int, character_ids_param.split(',')))  # Split and convert character IDs to a list of integers 
                print(character_ids)  # Print the converted character IDs (for debugging)
                filtered_data = data[data['Character ID'].isin(character_ids)].to_dict(orient='records')
                # Filter the data based on the provided character IDs and convert the result to a list of dictionaries
                
                # Check if the character ID requested is in the database
                if filtered_data:
                    return {'status': 200, 'response': filtered_data}, 200
                    # Return a JSON response with a status code 200 (OK) and the filtered data
                
                else:
                    return {'status': 404, 'response': 'No characters found for the provided IDs'}, 404
                    # Return a JSON response with a status code 404 (Not Found) and a message
            
            except ValueError:
                return {'status': 400, 'response': 'Invalid Character IDs provided'}, 400
                # If there is an error converting the character IDs to integers, return a JSON response with a status code 400 (Bad Request)
       
        # If receives Character Name
        else:
            if character_names_param:
                try:
                    print(character_names_param) # Print the received character (for debugging)
                    character_names = list(map(str, character_names_param.split(','))) # Split and convert character Names to a list of strings
                    print(character_names) # Print the converted character names (for debugging)
                    filtered_data = data[data['Character Name'].isin(character_names)].to_dict(orient='records')
                    # Filter the data based on the provided character Names and convert the result to a list of dictionaries
                    
                    # Check if the character name requested is in the database
                    if filtered_data: 
                        return {'status': 200, 'response': filtered_data}, 200
                        # Return a JSON response with a status code 200 (OK) and the filtered data
                    else:
                        return {'status': 404, 'response': 'No characters found for the provided Names'}, 404
                        # Return a JSON response with a status code 404 (Not Found) and a message

                except ValueError:
                    return {'status': 400, 'response': 'Invalid Character Names provided'}, 400
                    # If there is an error converting the character Names to Strings, return a JSON response with a status code 400 (Bad Request)

            data = data.to_dict(orient='records')  # Convert data to a dictionary
            return {'status': 200, 'response': data}, 200  # Return data and a 200 OK status

    def post(self):
        # Create a parser to handle request arguments
        parser = reqparse.RequestParser()
        # Character ID as mandatory argument
        parser.add_argument('Character ID', type=int, help='Missing argument or invalid Character ID', required=True)
        # Optional argument: Character Name, Total Available Events, Total Available Series, Total Available Comics, Price of the most expensive comics
        parser.add_argument('Character Name', type=str, help='Missing argument Character Name', required=False)
        parser.add_argument('Total Available Events', type=str, help='Missing argument Total Available Events', required=False)
        parser.add_argument('Total Available Series', type=str, help='Missing argument Total Available Series', required=False)
        parser.add_argument('Total Available Comics', type=int, help='Missing argument Total Available Comics', required=False)
        parser.add_argument('Price of the Most Expensive Comic', type=float, help='Missing argument Price of the Most Expensive Comic', required=False)
        # Access tokey key as mandatory argument
        parser.add_argument('access_token', type=str, help='access_token missing', required=True)
        
        args = parser.parse_args()  # Parse arguments into a dictionary
        # Check if the token is valid
        check=self.test_login(args['access_token'])
        if check[0]:
            return check
        print(check[1])
        # Check if for this user the scope POST is allowed
        if 'post' in check[1].lower(): 
            print('post passed')
        else:
            return {'status': 408, 'response': 'Unauthorized - Invalid scope'}, 408
        data = pd.read_csv('data.csv')  # Read data from a CSV file

        # Check if the provided character ID already exists in the dataset
        if args['Character ID'] in data['Character ID'].values:
            return {'status': 400, 'response': 'ID already exists'}, 400

        # Check if any of the optional character attributes are provided
        if any([args['Character Name']!=None, args['Total Available Events']!=None, args['Total Available Series']!=None, args['Total Available Comics']!=None]):
            # If one of the attributes is given, then it means that it does not have to be filled automatically and thus all attributes have to be in the request
            if not all([args['Character Name']!=None, args['Total Available Events']!=None, args['Total Available Series']!=None, args['Total Available Comics']!=None]):
                return {'status': 412, 'response': 'All fields are mandatory if they are not to be filled automatically.'}, 412
        
        else: # Retrieve data from Marvel API
            # Set up authentication and API details for the Marvel API (Public key, private key, URL, Timestamp)
            publicKey = '44e25f115205e6da5c303ac4bcdcaa48'
            privateKey = '06fa64d676c2aee53183896bcccc4c6613aa19c6'
            urlMARVEL = 'http://gateway.marvel.com'
            pathCharacters = '/v1/public/characters/'
            ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Calculate the MD5 digest of the authentication keys
            m5digest = hashlib.md5((ts + privateKey + publicKey).encode('utf-8')).hexdigest()
            urlMC = urlMARVEL + pathCharacters
            params = {'ts': ts, 'apikey': publicKey, 'hash': m5digest}

            # Make an HTTP GET request to fetch character information from the Marvel API
            response = requests.get(urlMC + str(args['Character ID']), params=params)

            if response.status_code != 200:
                return {'status': 404, 'response': 'Character not found'}, 404
                # If the response status code is not 200 (OK), return a JSON response indicating that the character was not found
            
            # Extract the JSON data under the key 'character'
            character = response.json()['data']['results'][0]
            pathCOMICS = '/v1/public/comics'

            # Check if the character has available comics
            if character['comics']['available'] != 0:
                # k times of request needed (given limit of 100 comics per request)
                k = math.ceil(character['comics']['available'] / 100) 
                list_comic_prices = []
                
                # Retrieve comic data in paginated requests (limit of 100 comics per request)
                for m in range(k): # every time of request, it retrieves data of maximum 100 comics from Marvel dataset
                    params = {'ts': ts, 'apikey': publicKey, 'hash': m5digest, 'characters': args['Character ID'], 'limit': 100, 'offset': m * 100}
                    response = requests.get(url=urlMARVEL + pathCOMICS, params=params).json()
                    
                    # Add every price of every comic books into the list
                    for comic in response['data']['results']:
                        for comic_price in comic['prices']:
                            list_comic_prices.append(comic_price['price'])
                    
                            # Calculate the price of the most expensive comic
                            price_most_expensive_comic = max(list_comic_prices)

            else: # If no available comics found in dataset, filled the maximum price value with None
                price_most_expensive_comic = None

            # Create a new entry for the character with retrieved information
            new_entry = {
                'Character ID': args['Character ID'],
                'Character Name': character['name'],
                'Total Available Events': character['events']['available'],
                'Total Available Series': character['series']['available'],
                'Total Available Comics': character['comics']['available'],
                'Price of the Most Expensive Comic': price_most_expensive_comic
            }

            # Add the new entry to the DataFrame and save it to the CSV file
            data.loc[len(data)] = new_entry

            # Save the modified DataFrame to the CSV file
            data.to_csv('data.csv', index=False)

            return {'status': 201, 'response': new_entry}, 201
            # Return a JSON response with a status code 201 (Created) and the new character entry

        # Add the new entry with the data given by the user to the DataFrame if not to be filled automatically
        new_entry = {
            'Character ID': args['Character ID'],
            'Character Name': args['Character Name'],
            'Total Available Events': args['Total Available Events'],
            'Total Available Series': args['Total Available Series'],
            'Total Available Comics': args['Total Available Comics'],
            'Price of the Most Expensive Comic': args['Price of the Most Expensive Comic'] if args['Price of the Most Expensive Comic'] and args['Total Available Comics'] else None
        }
        data.loc[len(data)] = new_entry
    
        # Save the modified DataFrame to the CSV file
        data.to_csv('data.csv', index=False)
    
        return {'status': 201, 'response': new_entry}, 201

    def put(self):
        # Create a request parser to handle and validate input parameters
        parser = reqparse.RequestParser()
        # Mandatory input parameters: Character ID (integer)
        parser.add_argument('Character ID', type=int, help='Missing argument Character ID', required=True)
        # Optional input parameters: Character name (string), available events (integer), available series (integer), available comics (integer), price of teh most expensive comic (float)
        parser.add_argument('Character Name', type=str, help='Missing argument Character Name', required=False)
        parser.add_argument('Total Available Events', type=int, help='Missing argument Total Available Events', required=False)
        parser.add_argument('Total Available Series', type=int, help='Missing argument Total Available Series', required=False)
        parser.add_argument('Total Available Comics', type=int, help='Missing argument Total Available Comics', required=False)
        parser.add_argument('Price of the Most Expensive Comic', type=float, help='Missing argument Price of the Most Expensive Comic', required=False)
        parser.add_argument('Currency', type=str, help='Missing argument Currency', required=False)
        # Mandarory input parameter: access token key (string)
        parser.add_argument('access_token', type=str, help='access_token missing', required=True)

        # Parse the request to extract and validate the provided parameters
        args = parser.parse_args()
        
        # Authenticate and authorize the user with the provided access_token
        check=self.test_login(args['access_token'])
        if check[0]: # Authentication: check access token
            return check
        print(check[1]) # Authorization: check if the request is asking for authorized function 'put'
        if 'put' in check[1].lower():
            print('put passed')
        else:
            return {'status': 408, 'response': 'Unauthorized - Invalid scope'}, 408
        
        # Read character data from the CSV file
        data = pd.read_csv('data.csv')# read CSV

        # Check if the provided character ID exists in the dataset
        if args['Character ID'] not in data['Character ID'].values:
            return {'status': 404, 'response': 'Character not found'}, 404
        
        # Update the corresponding entry in the DataFrame if applicable parameters are provided
        if args['Character Name'] or args['Total Available Events'] or args['Total Available Series'] or args['Total Available Comics'] or args['Price of the Most Expensive Comic']:
            # Find the relevant data with mandatory parameter "Character ID" inputted
            if args['Character Name']:
                data.loc[data['Character ID'] == args['Character ID'], 'Character Name'] = args['Character Name']
            
            if args['Total Available Events']:
                data.loc[data['Character ID'] == args['Character ID'], 'Total Available Events'] = args['Total Available Events']

            if args['Total Available Series']:
                data.loc[data['Character ID'] == args['Character ID'], 'Total Available Series'] = args['Total Available Series']

            if args['Total Available Comics']:
                data.loc[data['Character ID'] == args['Character ID'], 'Total Available Comics'] = args['Total Available Comics']
            
            if args['Price of the Most Expensive Comic']:
                # If the Currency attribute is given, then convert the price to USD and modify the value in the Dataframe
                if args['Currency']:
                    if args['Currency'] in ['USD', 'EUR', 'GBP', 'CAD']:
                        if args['Currency'] != 'USD':
                            
                            # Retrieve currency exchange rates from another API
                            exchange_api='dd4d98d37e41e59e13142b3a6aecd2cc'
                            url_exchange='http://api.exchangeratesapi.io/v1/latest'
                            params={'access_key':exchange_api}
                            if args['Currency'] != 'EUR':
                                rates_currency=requests.get(url_exchange, params=params).json()
                                print(rates_currency)
                                rates_currency=rates_currency['rates'][args['Currency']] # Get the exchange rate of requested currency
                            else:
                                rates_currency=1
                            rates_USD=requests.get(url_exchange, params=params).json()['rates']['USD']
                            
                            # Convert and update the price in the desired currency
                            args['Price of the Most Expensive Comic'] = args['Price of the Most Expensive Comic'] * rates_USD / rates_currency
                    
                    else:
                        return {'status': 412, 'response': 'Currency not supported'}, 412

                    
                data.loc[data['Character ID'] == args['Character ID'], 'Price of the Most Expensive Comic'] = args['Price of the Most Expensive Comic']
            
            if args['Total Available Comics'] == 0:
            # In this case the value of Total Available Comics is 0, so the value of Price of the Most Expensive Comic must be set to None
                data.loc[data['Character ID'] == args['Character ID'], 'Total Available Comics'] = args['Total Available Comics']
                data.loc[data['Character ID'] == args['Character ID'], 'Price of the Most Expensive Comic'] = None

            # Save the modified DataFrame to the CSV file
            data.to_csv('data.csv', index=False)

            # Return the modified entry as a response
            modified_entry = data[data['Character ID'] == args['Character ID']].to_dict(orient='records')[0]
            return {'status': 200, 'response': modified_entry}, 200
        else:
            return {'status': 410, 'response': 'No attributes given to update data.'}, 410
    
    def delete(self):
        # Create a request parser to handle and validate input parameters
        parser = reqparse.RequestParser()
        # Mandatory input parameters: access_token
        parser.add_argument('Character IDs', type=str, help='Character ID is missing', required=False)
        parser.add_argument('Character Names', type=str, help='Character Name is missing', required=False)
        parser.add_argument('access_token', type=str, help='access_token missing', required=True)
        
        # Parse the request to extract and validate the provided parameters
        args = parser.parse_args()
        
        # Authenticate and authorize the user with the provided access_token
        check=self.test_login(args['access_token'])
        if check[0]: # Authentication: check access token
            return check
        print(check[1]) # Authorization: check if the request is asking for authorized function ''
        if 'delete' in check[1].lower():
            print('delete passed')
        else:
            return {'status': 408, 'response': 'Unauthorized - Invalid scope'}, 408

        # Check if both Character IDs and Character Names are provided
        if args['Character IDs'] and args['Character Names']:
            return {'status': 407, 'response': 'Provide either the Character Names or IDs, but not both.'}, 407

        data = pd.read_csv('data.csv')# read CSV

        # If receives Character ID
        if args['Character IDs']:
            try:
                character_ids = list(map(int, args['Character IDs'].split(',')))  # Split and convert character IDs to a list of integers 
                
                for character_id in character_ids:
                    # Check if the provided character ID exists in the dataset
                    if character_id not in data['Character ID'].values:
                        return {'status': 404, 'response': 'Character ID ' + str(character_id) + ' not found'}, 404

                    # Delete the corresponding entry from the DataFrame
                    data.drop(data[data['Character ID'] == character_id].index, inplace=True)
                
                # Save the modified DataFrame to the CSV file
                data.to_csv('data.csv', index=False)

                # Return the modified dataset as a response
                modified_dataset = data.to_dict(orient='records')
                return {'status': 200, 'response': modified_dataset}, 200
            
            except ValueError:
                return {'status': 400, 'response': 'Invalid Character IDs provided'}, 400
                # If there is an error converting the character IDs to integers, return a JSON response with a status code 400 (Bad Request)
       
        # If receives Character Names
        else:
            if args['Character Names']:
                try:
                    character_names = list(map(str, args['Character Names'].split(',')))  # Split and convert Character Names to a list of Character Names
                    for character_name in character_names:
                        # Check if the provided Character Name exists in the dataset
                        if character_name not in data['Character Name'].values:
                            return {'status': 404, 'response': 'Character Name ' + character_name + ' not found'}, 404

                        # Delete the corresponding entry from the DataFrame
                        data.drop(data[data['Character Name'] == character_name].index, inplace=True)
                
                    # Save the modified DataFrame to the CSV file
                    data.to_csv('data.csv', index=False)

                    # Return the modified dataset as a response
                    modified_dataset = data.to_dict(orient='records')
                    return {'status': 200, 'response': modified_dataset}, 200
                
                except ValueError:
                    return {'status': 400, 'response': 'Invalid Character Names provided'}, 400
                    # If there is an error converting the character Names to strings, return a JSON response with a status code 400 (Bad Request)
            else:
                return {'status': 401, 'response': 'Character IDs or Character Names missing'}, 401
                # If both Character IDs and Character Names are missing, return a JSON response with a status code 400 (Bad Request)


# Define a resource for welcoming and checking if the server is working
class HelloWorld(Resource):
    def get(self):
        return {'status': 200, 
                'response': 'Welcome to the server! Please login.'}, 200

api.add_resource(HelloWorld, '/')
api.add_resource(LogIn, '/login')
api.add_resource(Characters, '/characters')

if __name__ == '__main__':
    app.run(debug=True)