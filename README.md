# CBLXKit

Framework to facilitate the development of Challenge Based Learning (CBL) systems and tools.

This repository contains the backend-only reference implementation used to run the framework experiment and validate backend extensions such as new domain attributes, strategy-based sorting, new phases, and JSON export.

## Prerequisites

1. Git installed
2. Python 3.10+ installed (Python 3.11 recommended)
3. pip installed
4. Optional: virtualenv (recommended)

## 1. Clone the repository

```bash
git clone https://github.com/jnecykdev/CBLXKit-Framework.git
cd CBLXKit-Framework
```
## 2. Create and activate a virtual environment

Linux or macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
```
Confirm you are using the virtual environment:

```bash
python --version
pip --version
```
## 3. Install dependencies

Upgrade pip:

```bash
python -m pip install --upgrade pip
```
Install requirements:

```bash
pip install -r requirements.txt
```

## 4. Environment variables

If the project uses environment variables, create a .env file in the project root. If you do not have a .env.example yet, create one so anyone can reproduce the setup.

Example .env (adapt to your settings.py):

```bash
DEBUG=True
SECRET_KEY=change-me
ALLOWED_HOSTS=127.0.0.1,localhost
```
If your settings require a database configuration (MySQL or others), also add the required variables, for example:

```bash
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
```
If you do not need a .env for your current setup, you can skip this section.

## 5. Database setup and migrations

Run migrations:

```bash
python manage.py migrate
```

## 6. Run the development server

```bash
python manage.py runserver
```
By default, the server will be available at:

http://127.0.0.1:8000/

## 7. Swagger UI and OpenAPI Schema

This project exposes an OpenAPI schema and interactive documentation using drf-spectacular.

Swagger UI:

http://127.0.0.1:8000/api/schema/swagger-ui/

OpenAPI schema (JSON):

http://127.0.0.1:8000/api/schema/

ReDoc:

http://127.0.0.1:8000/api/schema/redoc/

References:

drf-spectacular: https://github.com/tfranzel/drf-spectacular

DRF schemas: https://www.django-rest-framework.org/api-guide/schemas/

## 8. Minimal validation of the experiment environment

After opening Swagger UI, validate the environment with the following checks:

Swagger UI page loads successfully.

At least one endpoint is listed.

Perform at least one GET request using Swagger UI and confirm a 200 OK response.

If authentication is enabled, validate the expected response codes (401 Unauthorized or 403 Forbidden) for protected endpoints.

## 9. Experiment tasks roadmap

The experiment is executed by implementing and validating the following backend-only tasks in this order:

 - Add description field to the Project model.
 - Create and register an additional Strategy instance to sort projects alphabetically.
 - Introduce a new phase for Essential Questioning.
 - Export project pages and related content through structured JSON endpoints.

Each task must include:

 - Code implementation 
 - Database migration if required
 - Endpoint contract updates (serializers and views)

Validation using Swagger UI
