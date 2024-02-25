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

## Resources
- https://stackoverflow.com/questions/58794639/how-to-make-follower-following-system-with-django-model
- https://medium.com/analytics-vidhya/add-friends-with-689a2fa4e41d
- https://www.youtube.com/watch?v=diB38AvVkHw
- https://www.youtube.com/watch?v=Ae7nc1EGv-A
- https://github.com/mui/material-ui/blob/v5.15.10/docs/data/material/getting-started/templates/sign-in/SignIn.js