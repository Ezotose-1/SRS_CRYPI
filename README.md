This project is a PoC of an e-voting system using homomorphic encryption.

# How to use our project ?

Each file of this project is detailed in the sections below.

Our project uses the libraries **Pyfhel** (https://github.com/ibarrond/Pyfhel) and Flask.
```
pip install Flask
pip install Pyfhel
```

Once the libraries are installed you are ready to use our project.

First, you have to launch the server_auth.py and then the server_addition.py. An init request will be made to exchange public key (only) between servers.
The server_auth program needs the argument **--endtime** to work. This argument is the duration of the vote. In the example below, 60 means that the vote will be open for **60 seconds**. After this time, the voters will not be able to add their vote.
```

python server_auth.py --endtime 60

```

```

python server_addition.py

```

You can launch the client.py like this to make a vote and follow the instructions given by the program :

```

python client.py

```
To ask for the final results when the vote has ended, you can call the client.py with the -R or --result argument :
```
python client.py -R
```

# report

This folder contains our report explaining the use of the homomorphic encryption and the results of our experiments.

# slides

This folder contains the slides that will be presented during the final oral.

# src

This folder contains all the source code files of the project.

## client.py

This program is used by a voter to apply for a vote or to ask for the final results.

## database.py

This program is used to make computations on the database (db.json) to store tokens associated with a user (hash not reversible). The computations are checking if the token is valid or checking if the token has already voted or not.

## server_addition.py

This program is used to compute the votes. Each time a person votes, this server will increment the number of votes for the voted candidate. This server receives only encrypted votes and tokens from the voters (not the name of the voter). A voter's name **cannot** be recover using the token.

## server_auth.py

This program is used to provide a valid token and public key (for vote encryption on the client side) to the person who wants to vote. The voter only has to provide his name. This server also provides final results of the vote by asking the server_addition program for encrypted results and then decrypt the result to send it to the client.

