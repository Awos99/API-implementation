# Create an API with Authentification

### Documentation API


**Introduction**

This API provides authentication and access to character data, allowing users to perform various operations related to characters. Users can log in, retrieve character information, add new characters, update character data, and delete characters.

**Authentication**

Authentication is required to access certain endpoints of the API. It uses JSON Web Tokens (JWT) for user authentication. To authenticate, users must obtain an access token by providing a valid email and password through the **/login** endpoint. The access token is then included in the headers of subsequent requests to authenticate the user. The token is valid for 1 hour.

Main URL: http://127.0.0.1:5000

**Endpoints**
1. **Login**

  Send a GET request to login to the API and receive an access token that will be necessary for future requests.


*   **URL**: /login
*   **Method**: GET

*   **JSON Request Body**:
  *   **´email´** (string, required): The user's email address.
  *   **´password´** (string, required): The user's password.
*   **Response:**
  *   **´status´** (integer): The HTTP status code.
  *   **´response´** (string): A response message.
  *   **´access_token´** (string): An access token for authenticating subsequent requests.
* **Errors:**
  * **´401´** :
    * **'Unauthorized - Invalid password'**: The password entered is not correct.
    * **'Unauthorized - Invalid email'**: The email entered is not correct or it is empty.

2. **Characters**

  Endpoint used to interact with the database.

- **URL**: /characters
- **Methods**: GET, POST, PUT, DELETE
- **Authentication**: Required (access_token)
- **Errors：**
  - **405**: Token has expired.
  - **406**: Failed to decode token (Invalid signature or token）entered.
  - **407**: Failed to test validity of token.

**GET**

Retrieve data from the API's dataset.

- **´Method´**: **´GET´**
- **Query Parameters**:
  - **´access_token´** (string, required): The access token obtained during login.
  - **´Character IDs´** (string, optional if Character Names are provided): Comma-separated list of character IDs to filter by.
  - **´Character Names´** (string, optional if Character IDs are provided): Comma-separated list of character names to filter by.

  Send either 'Character IDs' or 'Character Names' in the request, but not both. If neither is sent then the entire dataset will be in the response.
- **´Response´**:
  - **´status´** (integer): The HTTP status code.
  - **´response´** (list): A list of character data.
    - Each character entry includes the following fields:
      - **´Character ID´** (integer): The unique identifier of the character.
      - **´Character Name´** (string): The name of the character.
      - **´Total Available Events´** (integer): The total number of events associated with the character.
      - **´Total Available Series´** (integer): The total number of series associated with the character.
      - **´Total Available Comics´** (integer): The total number of comics associated with the character.
      - **´Price of the Most Expensive Comic´** (float): The price of the most expensive comic associated with the character.
- **Errors:**
  - **407**: Provide either the Character Names or IDs, but not both.
  - **400**: Failed to convert Character IDs or Names.
  - **404**: No characters found for the provided Names or IDs.
  - **408**: User is not authorized to use this method.

**POST**

Add new data to the API's dataset.

- **Method**: **´POST´**
- **JSON Request Body**:
  - **´access_token´** (string, required): The access token obtained during login.
  - **´Character ID´** (integer, required): The unique identifier of the character.
  - **´Character Name´** (string, optional): The name of the character.
  - **´Total Available Events**´ (integer, optional): The total number of events associated with the character.
  - **´Total Available Series´** (integer, optional): The total number of series associated with the character.
  - **´Total Available Comics´** (integer, optional): The total number of comics associated with the character.
  - **´Price of the Most Expensive Comic´** (float, optional): The price of the most expensive comic associated with the character.

  If in the request only 'Character ID' and 'access_token' are sent, then the API will look for the character data automatically in the Marvel API.
- **Response**:
  - **´status´** (integer): The HTTP status code.
  - **´response´** (object): The added character data.
- **Errors:**
  - **400**: ID already exists.
  - **412**: All fields are mandatory if it is not to be filled automatically.
  - **408**: User is not authorized to use this method.
  - **404**: Character was not found in the Marvel API.


**PUT**

Modify data in the API's dataset.

- **Method**: **´PUT´**
- **JSON Request Body**:
  - **´access_token´** (string, required): The access token obtained during login.
  - **´Character ID´** (integer, required): The unique identifier of the character to update.
  - **´Character Name´** (string, optional): The updated name of the character.
  - **´Total Available Events´** (integer, optional): The updated total number of events associated with the character.
  - **´Total Available Series´** (integer, optional): The updated total number of series associated with the character.
  - **´Total Available Comics´** (integer, optional): The updated total number of comics associated with the character.
  - **´Price of the Most Expensive Comic´** (float, optional): The updated price of the most expensive comic associated with the character.
  - **´Currency´** (string, optional): The currency of the price (e.g., USD, EUR, GBP, CAD) for real-time currency conversion. USD as the default.
- **Response:**
  - **´status´** (integer): The HTTP status code.
  - **´response´** (object): The updated character data.
- **Errors:**
  - **404**: Character not found.
  - **412**: Currency not supported.
  - **410**: No attributes given to update data.
  - **408**: User is not authorized to use this method.

**DELETE**

Delete data from the API's dataset.

- **Method**: **´DELETE´**
- **JSON Request Body**:
  - **´access_token´** (string, required): The access token obtained during login.
  - **´Character IDs´** (string, optional): Comma-separated list of character IDs to delete.
  - **´Character Names´** (string, optional): Comma-separated list of character Names to delete.
- **Response**:
  - **´status´** (integer): The HTTP status code.
  - **´response´** (list): A list of character data after deletion (excluding the deleted character).
- **Errors:**
  - **404**: Character not found.
  - **408**: User is not authorized to use this method.
  - **407**: Provide either the Character Names or IDs, but not both.
  - **400**: Failed to convert either Character IDs or Names.
  - **401**: Character IDs or Character Names missing.

