import { postRequest } from "./Requests.jsx";

async function makeGithubCall(username) {
    let repData;
    var request;
    try {
        if (localStorage.getItem("etag") === null) {
            console.log("making a fresh request");
            request = new Request(`https://api.github.com/users/${username}/events/public`, {
                'method': 'GET',
                'X-GitHub-Api-Version': '2022-11-28',
                'Accept' : 'application/vnd.github+json'
            });
        } else {
            console.log("making new request");
            request = new Request(`https://api.github.com/users/${username}/events/public`, {
                'method': 'GET',
                'X-GitHub-Api-Version': '2022-11-28',
                'Accept' : 'application/vnd.github+json',
                'If-None-Match': `${localStorage.getItem("etag")}`
            });
        }
        repData = fetch(request).then((response) => {
            if (response.status === 200) {
                console.log(response.headers.get("etag"));
                localStorage.setItem("etag", response.headers.get("etag"));
                return response.json();
            } 
            else if (response.status === 304) {
                return "";
            }
            else {
                console.log("Something went wrong: " + response.status);
            }
        });
        return repData;
    } catch (error) {
        console.log(error);
    }
}

async function makeGithubPost(data, displayName, userId) {
    // save id of most recent event
    // post all the objects, otherwise go through list until id matches

    for (let item of data) {
        if (localStorage.getItem("githubID") === item.id) {
            break;
        } else {
            const body = {
                title: `Github ${item.event}`,
                description: `Github event for ${displayName}`,
                contentType: "text/markdown",
                content: `An event has occured at repository ${item.repo.name} by ${displayName} (Github username:${item.actor.display_login})`,
                visibility: "PUBLIC"
            };
            try {
                await postRequest(`authors/${userId}/posts/`, body);
            } catch (error) {
                console.log(error);
            }
        }
        
    }
}

async function pollGithub(github, displayName, userId, interval= 60000) {
    // get the username from the github field
    const username = github.split("/")[3];
    if (username !== undefined) {
        // if new user, fetch all information from the github api that is currently available
        var repData = await makeGithubCall(username);
        console.log(repData);
        if (localStorage.getItem("githubID") === null) {
            localStorage.setItem("githubID", repData[0].id);
        } 
        // else if (localStorage.getItem("githubID") !== repData[0].id) {
        //     makeGithubPost(repData, displayName, userId);
        //     localStorage.setItem("githubID", repData[0].id);
        // }
        
        // setTimeout(() => {
        //     pollGithub()
        // }, interval);
    }
}

export { pollGithub };