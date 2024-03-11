import { postRequest } from "./Requests.jsx";

async function makeGithubCall(username) {
    let repData;
    try {
        let request = new Request(`https://api.github.com/users/${username}/events/public`, {
            'method': 'GET',
            'X-GitHub-Api-Version': '2022-11-28',
            'Accept' : 'application/vnd.github+json'
        });
        repData = fetch(request).then((response) => {
            if (response.status === 200) {
                // FIGURE OUT WHY CORS IS NOT GIVING BACK HEADERS TO ME
              return response.json();
            } 
            else if (response.status === 200) {
                return "";
            }
            else {
              console.log("Something went wrong: " + response.status);
            }
        });
        // save etag in local storage here and foward it, also save most recent creation timestamp
        return repData;
        // this is for when I can save/get an etag from 
        //
        // repData = await new Request(`GET /users/${username}/events/public`, {
        //     headers: {
        //     'X-GitHub-Api-Version': '2022-11-28',
        //     'Accept' : 'application/vnd.github+json',
        //     'If-None-Match' : `${etag}`
        //     }
        // })
    } catch (error) {
        console.log(error);
    }
}

async function makeGithubPost(data, displayName, userId) {
    // save id of most recent event
    // post all the objects, otherwise go through list until id matches

    for (let item of data) {
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
        // if (id == item.id) {
        //     break;
        // }
    }
}

async function pollGithub(github, displayName, userId, interval= 60000) {
    // fetch author github information
    // local storage
    // get the username from the github field
    const username = github.split("/")[3]
    console.log(username);
    // if new user, fetch all information from the github api that is currently available
    var repData = await makeGithubCall(username);
    console.log(repData);

    // setTimeout(() => {
    //     pollGithub()
    // }, interval);
    
}

export { pollGithub };