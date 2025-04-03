# IoT Data Processing

By Pongphun Sakdasawit

![Preview](/assets/preview.png)

## Data cleaning & anomaly detection explanation

The data cleaning and anomaly detection process is done in the backend using Python. The process is as follows:

1. I imagined that sensor will send data every `N` minutes. by calling the POST `/sensor/data` endpoint. No matter what the data looks like, I will save it to the database. But the data should be in the following format:
    ```json
    {
        "temperature": N,
        "humidity": N,
        "air_quality": N
    }
    ```

2. In cleaning process, If that record has a `None` value, I will not use that record. Because I think that record maybe damaged or not valid. And if that record duplicated with other record, I will use one of them. Other than that, I consider that record can be used.

3. In anomaly detection process, I will use the `Z-Score` method to detect anomaly. `Z-Score` maybe not the best method to detect anomaly but it is simple and easy to understand. If the Z-Score of that record is greater than `3`, I will consider that record as an anomaly. because generally mean + 3sd or mean - 3sd is around 99.7% of the data. So if some record is greater than that, I will consider that record as an anomaly. Example in the image above at 6PM-7PM you can see that the most temperature is around 22-28 degrees. In that 1 hour, the temperature suddenly increased to 34 degrees. which is very weird. So I will consider that record as an anomaly.

## API Documentation

You can import `assets/IOT.postman_collection.json` into Postman to see the API documentation.

## How to run

Make sure you have Docker and Docker Compose installed on your machine.

```bash
docker-compose up
```

## Setup for local development

### Database

You can use your own database but I recommend using docker-compose

```yml
version: '3.8'

services:
  mysql:
    image: mysql:latest
    container_name: mysql_server
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: password
      MYSQL_DATABASE: sensordb
      MYSQL_USER: dbuser
      MYSQL_PASSWORD: password
      MYSQL_ALLOW_PUBLIC_KEY_RETRIEVAL: "true"
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql

volumes:
  mysql_data:
```

Then run the following command to start the database:

```bash
docker-compose up -d
```

Next, you can import initial data into the database. Use the `assets/sensor_data.csv` file to import data into the database. You can use any MySQL client to do this. For example, you can use MySQL Workbench or DBeaver.


### Backend

Make sure you have Python (My version is 3.12.9) and pip installed on your machine.

```bash
# Create a virtual environment (optional but recommended)
pip install virtualenv
python -m venv env
source env/bin/activate  # On Windows use `env\Scripts\activate.bat`
```

Then install the required packages:

```bash
pip install -r requirements.txt
```

Then run the backend server:

```bash
python manage.py runserver
```

This will start the server at [http://localhost:8000](http://localhost:8000).

> Note: If you are using my docker-compose to run database, you don't need to do anything for database setup. But if you run your own database, you need to edit the `settings.py` file in the `backend` directory to connect to your database.

### Frontend

Make sure you have Node.js (My version 22.14.0) and npm (My version 10.9.2) installed on your machine.

```bash
cd frontend

npm install
```

Then add a `.env` file in the root of the `frontend` directory with the following content:

```env
VITE_API_URL=http://localhost:8000/
```

Then run the development server:

```bash
npm run dev
```

See the app in your browser at [http://localhost:5173](http://localhost:5173).
