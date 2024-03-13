import React, { useState } from "react";
import {
	getRequest,
	postRequest,
	deleteRequest,
	putRequest,
} from "../utils/Requests.jsx";
import { Link } from "react-router-dom";

//Card modified from this source: https://flowbite.com/docs/components/card/ Accessed Feb 10th
//Buttons modified from this source: https://flowbite.com/docs/components/button-group/ Accessed Feb 10th

function ProfileCard({
	key,
	url,
	host,
	username,
	imageSrc,
	github,
	buttontype,
	authId = "",
	owner,
	viewerId = "",
	altId = "",
	changeProfileFunc,
	change,
}) {
	//authId is just author/"host" page's uuid, key is the id of the profile card being displayed
	//altId is a copy of authId that won't be considered/operated on
	//owner -- true if person viewing is the owner of the profile, false if not.
	//viewerId is the id of the person viewing the page, useful for distinguishing, used for displaying card of the actual owner.

	let cardUUID = "";
	const [showCard, setShowCard] = useState(true); //IF A FOLLOWER IS UNFOLLOWED OR REQUEST DEALT WITH, THIS WILL BE CHANGED AS TO NOT SHOW IT? HOPEFULLY?

	if (authId != "") {
		let parts = url.split("/");
		cardUUID = parts[parts.length - 1];
		console.log("UUID IN CARD: ", cardUUID);
	} else {
		cardUUID = altId; //the user and author's ID
	}

	//API METHODS BEGIN

	const follow = (authorUUID, followerUUID) => {
		var dataToSend = {
			type: "inbox",
			author: `http://127.0.0.1:5454/authors/${authorUUID}`,
			items: [
				{
					type: "Follow",
					actor: {
						type: "author",
						id: `http://127.0.0.1:5454/authors/${followerUUID}`,
					},
					object: {
						type: "author",
						id: `http://127.0.0.1:5454/authors/${authorUUID}`,
					},
				},
			],
		};
		postRequest(`authors/${authorUUID}/inbox`, dataToSend)
			.then((data) => {
				console.log("Follow Req POSTed.");
			})
			.catch((error) => {
				console.log("ERROR: ", error.message);
			});
	};

	const unfollow = (removerUUID, removeeUUID) => {
		deleteRequest(`authors/${removeeUUID}/followers/${removerUUID}`)
			.then((data) => {
				console.log("DELETE");
				setShowCard(false);
			})
			.catch((error) => {
				console.log("ERROR: ", error.message);
			});
	};

	const request = (authorUUID, requesterUUID, decision) => {
		deleteRequest(`authors/${authorUUID}/followrequests/${requesterUUID}`)
			.then((data) => {
				console.log("Reject Request:", data);
			})
			.catch((error) => {
				console.log("ERROR: ", error.message);
			});

		if (decision === true) {
			//accepting new follower
			putRequest(`authors/${authorUUID}/followers/${requesterUUID}`)
				.then((data) => {
					console.log("Request Accepted, PUT DATA:", data);
				})
				.catch((error) => {
					console.log("ERROR: ", error.message);
				});

			setShowCard(false);
		} else {
			//declining new follower
			setShowCard(false);
		}
	};

	//API METHODS END

	return (
		<div>
			{showCard && (
				<a
					href="#"
					className="self-center mx-72 w-96 h-48 flex flex-col items-center bg-white border border-gray-200 rounded-lg shadow md:flex-row md:max-w-xl dark:border-white-700 dark:bg-white-800"
				>
					<img
						className="object-cover ml-2 mr-1 w-full max-w-40 max-h-40 min-w-40 min-h-40 rounded-t-lg h-96 md:h-auto md:w-48 md:rounded-none md:rounded-s-lg"
						src={imageSrc}
						alt=""
					></img>

					<div className="flex flex-col justify-between p-4 leading-normal">
						<h5 className="mb-2 text-2xl font-bold tracking-tight text-black-900 dark:text-black">
							{username}
						</h5>

						{buttontype === "Follow" && !owner && (
							<button
								onClick={() => follow(altId, viewerId)}
								class="text-white bg-slate-800 hover:bg-orange-500 focus:bg-orange-600 font-medium rounded-lg text-sm px-1 py-1 focus:outline-none dark:focus:bg-orange-500"
							>
								Req. Follow
							</button>
						)}

						{buttontype === "Following" && owner && (
							<button
								onClick={() => unfollow(authId, cardUUID)}
								class="text-white bg-slate-800 hover:bg-orange-500 focus:bg-orange-600 font-medium rounded-lg text-sm px-1 py-1 focus:outline-none dark:focus:bg-orange-500"
							>
								Unfollow
							</button>
						)}

						{buttontype === "Request" && owner && (
							<div className="flex flex-col space-y-1">
								<button
									onClick={() => request(authId, cardUUID, true)}
									class="text-white bg-slate-800 hover:bg-orange-500 focus:bg-orange-600 font-medium rounded-lg text-sm px-1 py-1 focus:outline-none dark:focus:bg-orange-500"
								>
									Accept
								</button>
								<button
									onClick={() => request(authId, cardUUID, false)}
									class="text-white bg-slate-800 hover:bg-orange-500 focus:bg-orange-600 font-medium rounded-lg text-sm px-1 py-1 focus:outline-none dark:focus:bg-orange-500"
								>
									Decline
								</button>
							</div>
						)}

						{
							<Link
								onClick={() => changeProfileFunc(change)}
								to={`/profile/${cardUUID}/`}
							>
								Profile
							</Link>
						}
					</div>
				</a>
			)}
		</div>
	);
}

export default ProfileCard;
