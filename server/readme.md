Node.js Server Setup Guide
This guide will walk you through the steps required to set up and run the Node.js server for your project. The server interacts with a database and imports data to provide the necessary functionality.

Prerequisites
Node.js: Make sure you have Node.js installed on your system. You can download it from the official Node.js website: https://nodejs.org/

Download dependencies
-Run `npm i`

Setting up the Database
-Navigate to the database folder:

-Run the SQL script to create the database:
Open your preferred SQL client (e.g., MySQL Workbench, pgAdmin for PostgreSQL).
Connect to your local or remote database server.
Open the DB web dev.sql script located in the database folder.
Execute the script to create the necessary database structure.
Importing Data to the Database
From the database folder, run the following command to import data to the database:

Importing Data to the Database
-From the database folder, run the following command to import data to the database:

Starting the Node.js Server
Go back to the root directory of your project:
Start the Node.js server: -`npm start`
