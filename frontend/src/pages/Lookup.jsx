import "./Lookup.css";
import React, {useEffect, useState} from "react";
import {getRequest, postRequest} from "../utils/Requests.jsx";
import {useAuth} from "../utils/Auth.jsx";
import ProfileCard from "../components/ProfileCard.jsx";

function Lookup() {
    const auth = useAuth();
    const [authors, setAuthors] = useState([]);
    const [following, setFollowings] = useState([]);
    const [followRequests, setFollowRequests] = useState([]);
    const [followers, setFollowers] = useState([]);
    const [sentFollowRequests, setSentFollowRequests] = useState([]);

    const getIdList = (authorList) => {
        return authorList.map((author) => {
            return author.id;
        });
    }

    useEffect(() => {
        getRequest("remote-authors/")
            .then((data) => {
                console.log("GET authors Request Data:", data);
                setAuthors(data.items);
            })
            .catch((error) => {
                console.log("ERROR: ", error.message);
            });
    }, []);

    useEffect(() => {
        getRequest(`authors/${auth.user.id}/followings`)
			.then((data) => {
				console.log("GET followings Request Data:", data);
                let followingIdList = getIdList(data.items);
				setFollowings(followingIdList);
			})
			.catch((error) => {
				console.log("ERROR: ", error.message);
			});
    }, []);

    useEffect(() => {
        getRequest(`authors/${auth.user.id}/followers`)
            .then((data) => {
                console.log("GET followers Request Data:", data);
                let followerIdList = getIdList(data.items);
                setFollowers(followerIdList);
            })
            .catch((error) => {
                console.log("ERROR: ", error.message);
            });
    }, []);

    useEffect(() => {
        getRequest(`authors/${auth.user.id}/followrequests`)
            .then((data) => {
                console.log("GET followrequests Request Data:", data);
                let followRequestIdList = getIdList(data.items);
                setFollowRequests(followRequestIdList);
            })
            .catch((error) => {
                console.log("ERROR: ", error.message);
            });
    }, []);

    useEffect(() => {
        getRequest(`authors/${auth.user.id}/sentFollowRequests`)
            .then((data) => {
                console.log("GET sentfollowrequests Request Data:", data);
                let sentFollowRequestIdList = getIdList(data.items);
                setSentFollowRequests(sentFollowRequestIdList);
            })
            .catch((error) => {
                console.log("ERROR: ", error.message);
            });
    }, []);

    return (
        <div className="lookup-container">
            {authors.map((author) => {
                // button type will be Follow if the author is not in the following list and not in the follow requests list
                // button type will be Following if the author is in the followings list
                // button type will be Requested if the author is in the follow requests list

                let buttontype = "";
                if (following.includes(author.id)) {
                    buttontype = "Following";
                } else if (followRequests.includes(author.id)) {
                    buttontype = "Requested";
                } else if (!sentFollowRequests.includes(author.id)){
                    buttontype = "Follow";
                }
                const authorId = author.id.split("/").slice(-1)[0]; // extract the author's id
                return (
                    <ProfileCard
                    // author = remote author here
                        key={author.id}
                        url = {author.url}
                        host = {author.host}
                        username={author.displayName}
                        imageSrc={author.profileImage}
                        authId={auth.user.id}
                        github={author.github}
                        owner={false}
                        viewerId={auth.user.id}
                        altId={authorId}
                        showLink={false}
                        buttontype={buttontype}
                    />
                );
            })}
        </div>
    );
}

export default Lookup;