# WADAS Web Interface


This guide provides the necessary steps to install dependencies and to run the project.

## Prerequisites
Ensure you have the following installed on your system:
- [Node.js](https://nodejs.org/) (LTS version recommended)
- [npm](https://www.npmjs.com/) (comes with Node.js)

## Installation Steps
1. **Clone the Repository** (if applicable):
   ```sh
   git clone <repository-url>
   cd <project-folder>
   ```
2. **Install Dependencies** using npm in the project  root folder:
   ```sh
   npm install
   ```

## Running the Project - Standalone
To start the development server, run:
```sh
npm start
```
This will launch the React application in your default browser.

## Running the Project inside WADAS WebServer
- Build the project using npm in the project root folder:
```sh
npm run build
  ```
- Copy the content of ```build/``` directory under ```%WADAS_ROOT%/wadas_webserver/frontend/```


- Start the webserver using the WADAS GUI.


- Visit ```https://localhost``` with your browser.


## Troubleshooting
- If you encounter errors related to dependencies, try removing and reinstalling them:
  ```sh
  rm -rf node_modules package-lock.json
  npm install
  ```

