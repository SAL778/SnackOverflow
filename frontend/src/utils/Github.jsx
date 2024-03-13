import { postRequest } from "./Requests.jsx";

async function makeGithubCall(username) {
    let repData;
    var request;
    // attempt a github api call
    try {
        if (localStorage.getItem("etag") === null) {
            // completely first poll, need to cache the etag after this
            console.log("making a fresh request");
            request = new Request(`https://api.github.com/users/${username}/events/public`, {
                'method': 'GET',
                'headers':{
                    'X-GitHub-Api-Version': '2022-11-28',
                    'Accept' : 'application/vnd.github+json'
                }
            });
        } else {
            // have already fetched from before, will validate for any new changes
            console.log("checking for updates");
            request = new Request(`https://api.github.com/users/${username}/events/public`, {
                'method': 'GET',
                'headers': {
                    'X-GitHub-Api-Version': '2022-11-28',
                    'Accept' : 'application/vnd.github+json',
                    'If-None-Match': `${localStorage.getItem("etag")}`
                }
            });
        }
        repData = fetch(request).then((response) => {
            // check if changes have been made
            if (response.status === 200) {
                localStorage.setItem("etag", response.headers.get("etag"));
                return response.json();
            } 
            // no changes are detected
            else if (response.status === 304) {
                return "no change";
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
    // go through the log of event data, if there is duplicate events, break out of loop
    for (let item of data) {
        if (localStorage.getItem("githubID") === item.id) {
            break;
        } else {
            // create post content for github activity
            const body = {
                title: `Github ${item.type}`,
                description: `Github event for ${displayName}`,
                contentType: "text/markdown",
                content: `An ${item.type} event has occured at repository ${item.repo.name} (Github username: ${item.actor.display_login})`,
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

async function pollGithub(github, displayName, userId, interval) {
    // get the username from the github field
    const username = github.split("/")[3];
    if (username !== undefined && github.split("/")[2] === "github.com" && username !== "") {
        // fetch from the github server and check to see if any changes are made
        var repData = await makeGithubCall(username);
        console.log(repData);
        // make posts if new data is found
        if (repData !== "no change" && repData !== undefined) {
            if (localStorage.getItem("githubID") === null || (localStorage.getItem("githubID") !== repData[0].id)) {
                // make all the new github activity posts when given results
                await makeGithubPost(repData, displayName, userId);
                localStorage.setItem("githubID", repData[0].id);
            } 
        }
        if (localStorage.getItem("isLoggedIn")=== "true") {
            console.log("should trigger multiple times until logged out");
            setTimeout(() => {
                pollGithub(github, displayName, userId)
            }, interval);
        }
        
    }
}

export { pollGithub };