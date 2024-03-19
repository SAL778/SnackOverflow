# CMPUT404-project-socialdistribution

CMPUT404-project-socialdistribution

See [the web page](https://uofa-cmput404.github.io/general/project.html) for a description of the project.

Make a distributed social network!

# Contributors / Licensing

## Contributors

Team Members:

- Saahil Rachh (rachh)
- Larissa Zhang (ltzhang)
- Soodarshan Gajadhur (gajadhur)
- Dylan Clarke (dclarke)
- Tauseef Nafee Fattah (fattah)

## Licensing

Generally everything is LICENSE'D under the Apache 2 license by Abram Hindle.

All text is licensed under the CC-BY-SA 4.0 http://creativecommons.org/licenses/by-sa/4.0/deed.en_US

## Extra citations

For our logo "Snack Overflow", the original source image comes from a reply to the original post by u/Roadcrosser at this [link](https://www.reddit.com/r/ProgrammerHumor/comments/2vadys/comment/cofylak/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button) accessed 2024-02-22. The direct link to the image is available [here](https://i.imgur.com/jSUHoMZ.png).

## Getting Started

First, install all the dependencies by running:
```bash
npm install
# or
npm i
```

Then, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```
Open [http://localhost:8000](http://localhost:8000) with your browser to see the result.

For running the django server, have an venv set up at root and install all packages with pip using requirements.txt.
To have static files served locally, go to the frontend/ folder, install all packages with `npm i` and run `npm run build` to build a dist/folder.
Then you can at backend/ `python manage.py runserver` to see the server work properly.
For testing, you can use `python manage.py test` to get all the tests running. 

To deploy remotely, look at the deployment steps at the top level of the repo.

## Resources
- Django Serializers: https://www.django-rest-framework.org/api-guide/serializers/
- https://stackoverflow.com/questions/58794639/how-to-make-follower-following-system-with-django-model
- https://medium.com/analytics-vidhya/add-friends-with-689a2fa4e41d
- https://www.youtube.com/watch?v=diB38AvVkHw
- https://www.youtube.com/watch?v=Ae7nc1EGv-A
- https://github.com/mui/material-ui/blob/v5.15.10/docs/data/material/getting-started/templates/sign-in/SignIn.js
- https://github.com/heroku/heroku-buildpack-nodejs/issues/385
- https://github.dev/TonyTony999/scrape_2/blob/master/package.json
- https://stackoverflow.com/questions/68590569/heroku-deploy-with-vitejs-error-h10-vite-not-found
- https://elements.heroku.com/buildpacks/heroku/heroku-buildpack-nodejs
- https://stackoverflow.com/questions/51187161/deploy-an-app-to-heroku-that-isnt-in-the-project-root
- https://www.youtube.com/watch?v=fbIFdWj8PsY - Utilized this youtube video to understand how to implement swagger documentation with custom descriptions
- GitHub-Co-pilot helped write the descriptions of the functions for swagger documentation used in views.py (Inside the backend folder)
- https://dev.to/mdrhmn/deploying-react-django-app-using-heroku-2gfa - Utilized this document to understand how to deploy the app. Some of the code was used in settings.py (backend folder)
- https://vonkunesnewton.medium.com/understanding-static-files-in-django-heroku-1b8d2f003977 - Utilized this document to debug the deployment and serve static files
- DjangoAuthentication: https://www.youtube.com/watch?v=diB38AvVkHw
- DjangoAuthentication: https://github.com/dotja/authentication_app_react_django_rest/tree/main
- Custom User Model: https://www.youtube.com/watch?v=Ae7nc1EGv-A
- Custom User Model: https://github.com/veryacademy/YT-Django-Theory-Create-Custom-User-Models-Admin-Testing
- Sign-in page template: https://github.com/mui/material-ui/blob/v5.15.10/docs/data/material/getting-started/templates/sign-in/SignIn.js
- For deployment: https://github.com/heroku/heroku-buildpack-nodejs/issues/385
- For deployment: https://github.dev/TonyTony999/scrape_2/blob/master/package.json
- For deployment: https://stackoverflow.com/questions/68590569/heroku-deploy-with-vitejs-error-h10-vite-not-found
- For deployment: https://elements.heroku.com/buildpacks/heroku/heroku-buildpack-nodejs
- For deployment: https://stackoverflow.com/questions/51187161/deploy-an-app-to-heroku-that-isnt-in-the-project-root
