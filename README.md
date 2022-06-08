# Ecommerce Django App

Rest API using DRF to emulate a limited e-commerce functionality.

## Postman collection

In the link below you can test the endpoints. The app is deployed in PythonAnywhere. For testing in local, the URL variable inside postman must be changed.

`https://www.getpostman.com/collections/76d6f5b9899bf18392c9`

The app requires authorization. The endpoint to create a token is inside the JWT folder. The token is saved in a variable, so there is no need to copy it to each endpoint header.

## Deployment
### PythonAnywhere deploy

The app is running on `marcosmalvarez.pythonanywhere.com`

### Local deploy

Some data is cached in the database. To create the cache database, it is requires to execute the command:

```bash
python manage.py createcachetable
```
