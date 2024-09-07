To run the Flask app using Uvicorn, you can use the following command:

```bash
uvicorn pantry.api:app
```

This assumes that your `api.py` file is located in the `pantry` folder and that your Flask app object is named `app`.

To run the Flask app using the `flask run` command, you can use the following command:

```bash
FLASK_APP=Flask/main.py flask run
```

This assumes that your `main.py` file is located in the `Flask` folder.

Remember to make sure that you have all the necessary dependencies installed and that you are in the correct directory before running these commands.
