This provides aramaic translations.

It's a vercel app with:
- next.js react front end
- python flask/vercel serverless backend

# Running locally
## Front end
run the front end with

    npm run dev
## back end
change the fetch url (pages/index.js line 24 needs `api/translator` to be changed to `http://localhost:5000/api/translator`). Do not commit this change.
run the backend with 

    FLASK_APP=api/translator.py flask run
