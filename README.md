# Scircula API

## Installation
```
docker-compose up
```

The API documentation can be accessed at: (http://localhost:9000/swagger/).

## Development

Add a library:
```
docker-compose exec api pip install -r requirements.txt
```
Apply migrations:
```
docker-compose exec api python manage.py migrate
```
Create a super user:
```
python manage.py createsuperuser --username=admin --email=admin
```
Create an app 
```
docker-compose exec api django-admin startapp customers
sudo chown -R antoine:antoine .
```
Save data as fixtures:
```
docker-compose exec api python manage.py dumpdata  > fixtures.json
```

Load demo data:
```
docker-compose exec api python manage.py loaddata core/fixtures.json
```

## Contiuous Deployment

The API is automatically deployed on AWS Elastic Container Service with Gitlab CI.
