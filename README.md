# Django Application

This is a Django web application for [describe your application here].

## Installation

Follow these steps to set up and run the application:

### Prerequisites

- Python 3.9 or higher
- Docker (optional, for running in Docker)

### 1. Clone the Repository

Clone this repository to your local machine:

```bash
git clone https://github.com/heenassharma/social_networking_assignment.git
cd social_networking_assignment
```

### 2. Create a Virtual Environment (Optional)

It's recommended to create a virtual environment for the project to isolate dependencies:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

### 3. Install Dependencies

Install the Python dependencies using pip:

```bash
pip install -r requirements.txt
```

### 4. Run Migrations

Apply database migrations to create the database schema:

```bash
python manage.py migrate
```

### 5. Start the Development Server

Start the Django development server:

```bash
python manage.py runserver
```

The application will be accessible at http://localhost:8000/.

### (Optional) Running with Docker

You can also run the application using Docker. Make sure Docker is installed on your system.

```bash
docker-compose up --build
```

The application will be accessible at http://localhost:8000/.

### Testing the Application

1. Import the postman collection provided in the file Social App.postman_collection.json 
2. Start with the Signup and Login API
3. After login, update the access token in the token variable of the collection to run the rest of the APIs
4. In the APIs where id/pk is required in the URL, replace the correct id/pk to successfully run the API