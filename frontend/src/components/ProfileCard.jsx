import React, { useState } from "react";
import {
	getRequest,
	postRequest,
	deleteRequest,
	putRequest,
} from "../utils/Requests.jsx";
import { Link } from "react-router-dom";
import { useAuth } from "../utils/Auth.jsx";
import defaultPFP from "../assets/smiley.jpg";

//Card modified from this source: https://flowbite.com/docs/components/card/ Accessed Feb 10th
//Buttons modified from this source: https://flowbite.com/docs/components/button-group/ Accessed Feb 10th

function ProfileCard({
	// key,
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
	showLink = true,
}) {
	//authId is just author/"host" page's uuid, key is the id of the profile card being displayed
	//altId is a copy of authId that won't be considered/operated on
	//owner -- true if person viewing is the owner of the profile, false if not.
	//viewerId is the id of the person viewing the page, useful for distinguishing, used for displaying card of the actual owner.

	const auth = useAuth();

	imageSrc = imageSrc || defaultPFP

	let cardUUID = "";
	const [showCard, setShowCard] = useState(true); //IF A FOLLOWER IS UNFOLLOWED OR REQUEST DEALT WITH, THIS WILL BE CHANGED AS TO NOT SHOW IT? HOPEFULLY?
	console.log("IMAGEEEEE", imageSrc);
	if (authId != "") {
		let parts = url.split("/");
		cardUUID = parts[parts.length - 1];
		console.log("UUID IN CARD: ", cardUUID);
	} else {
		cardUUID = altId; //the user and author's ID
	}

	//API METHODS BEGIN
	// TODO author needs to be full URL from author object, not just ID
	// sending a follow request object to the object's inbox
	const follow = (receivingId, sendingId) => {
		var dataToSend = {
			type: "inbox",
			// only the uuids are used by the backend, so, the first part of the url is just dummy data
			author: `http://127.0.0.1:5454/api/authors/${receivingId}`,
			items: [
				{
					type: "Follow",
					actor: {
						type: "author",
						// auth.user.id == sendingId, the person sending the request
						id: `http://127.0.0.1:5454/api/authors/${sendingId}`,
						host: auth.user.host,
						displayName: auth.user.displayName,
						url: auth.user.url,
						github: auth.user.github,
						profileImage: auth.user.profileImage,
					},
					object: {
						type: "author",
						id: `http://127.0.0.1:5454/api/authors/${receivingId}`,
						host: host,
						displayName: username,
						url: url,
						github: github,
						profileImage: imageSrc,
					},
				},
			],
		};
		postRequest(`authors/${receivingId}/inbox`, dataToSend)
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

	const renderButton = (onClick, text) => (
		<button
			onClick={onClick}
			class="text-white bg-slate-800 hover:bg-orange-500 focus:bg-orange-600 font-medium rounded-lg text-sm px-1 py-1 focus:outline-none dark:focus:bg-orange-500"
		>
			{text}
		</button>
	);

	return (
		<div>
			{showCard && (
				<a
					href="#"
					className="self-center mx-72 w-[450px] h-48 flex flex-col items-center bg-white border border-gray-200 rounded-lg shadow md:flex-row md:max-w-xl dark:border-white-700 dark:bg-white-800"
				>
					<img
						className="object-cover ml-2 mr-1 w-full max-w-40 max-h-40 min-w-40 min-h-40 rounded-t-lg h-96 md:h-auto md:w-48 md:rounded-none md:rounded-s-lg"
						src={imageSrc}
						alt=""
					></img>

					<div className="flex flex-col justify-between p-4 leading-normal w-[150px]">
						<h5 className="mb-2 text-2xl font-bold tracking-tight text-black-900 dark:text-black">
							{username}
						</h5>

						{buttontype === "Follow" &&
							!owner &&
							renderButton(() => follow(altId, viewerId), "Req. Follow")}
						{buttontype === "Following" &&
							owner &&
							renderButton(() => unfollow(authId, cardUUID), "Unfollow")}
						{buttontype === "Request" && owner && (
							<div className="flex flex-col space-y-1">
								{renderButton(() => request(authId, cardUUID, true), "Accept")}
								{renderButton(
									() => request(authId, cardUUID, false),
									"Decline"
								)}
							</div>
						)}
						{showLink && (
							<Link
								onClick={() => {
									if (changeProfileFunc) {
										changeProfileFunc(change);
									}
								}}
								to={`/profile/${cardUUID}/`}
							>
								Profile
							</Link>
						)}
					</div>
				</a>
			)}
		</div>
	);
}

export default ProfileCard;
