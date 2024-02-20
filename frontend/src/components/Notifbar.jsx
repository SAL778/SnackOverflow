import React from "react";

const followType = "follow";
const commentType = "comment";
const likeType = "like";

function Notifications() {
	// set up promises to send request object to inbox
	// how to ensure that you get the correct author id?
	// var request = Request(path.join(window.location,"authors", authorid, "inbox"))
	// React.useEffect(() => {
	// 	fetch(request)
	// 	.then(response => response.json())
	// 	.catch(error => console.error(error));
	// });

	const followObject = {
		type: "follow",
		summary: "Greg wants to follow you",
		author: {
			displayName: "Greg Johnson",
			id: "followeeURL",
			url: "followeeURL"
		},
		object: {
			id: "authorURL",
			url: "authorURL"
		}
	};
	const commentObject = {
		type: "comment",
		author: {
			displayName: "Greg Johnson",
			id: "followeeURL",
			url: "followeeURL"
		},
		published: "",
		id: "commentURL"
	};
	const likeObject = {
		type: "like",
		summary: "Greg likes your post",
		author: {
			displayName: "Greg Johnson",
			id: "followeeURL",
			url: "followeeURL"
		},
		object: "PostorCommentURL"
	};
	// not sure how the inbox object will be serialized so this is temporary
	var inbox = [followObject, commentObject, likeObject, commentObject, commentObject, commentObject, commentObject];
	var allNotifs = [];

	// building the feed for all the objects in the inbox
	for (let object of inbox) {
		const author = object.author;
		const keyIndex = inbox.indexOf(object);
		if (object.type === followType) {
			allNotifs.push(
				<div key={keyIndex} className="flex flex-initial rounded-md shadow-md bg-orange-300/75 p-3 m-2">
					<p className="text-sm">
						<a href={author.url} className="font-semibold hover:underline hover:text-orange-700">
						{author.displayName}
						</a>
						{" "} wants to follow you.
					</p>
				</div>
			)
		} 
		else if (object.type === likeType) {
			allNotifs.push(	
				<div key={keyIndex} className="flex flex-initial rounded-md shadow-md bg-orange-300/75 p-3 m-2">
					<p className="text-sm">
						<a href={author.url} className="font-semibold hover:underline hover:text-orange-700">
							{author.displayName}
						</a>
						{" "}left a like on your {" "}
						<a href={object.object} className="font-semibold hover:underline hover:text-orange-700">
							post
						</a>
						.
					</p>
				</div>
			)
		} else if (object.type === commentType) {
			allNotifs.push(	
				<div key={keyIndex} className="flex flex-initial rounded-md shadow-md bg-orange-300/75 p-3 m-2">
					<p className="text-sm">
						<a href={author.url} className="font-semibold hover:underline hover:text-orange-700">
							{author.displayName}
						</a>
						{" "} left a comment on your {" "}
						<a href={object.id} className="font-semibold hover:underline hover:text-orange-700">
							post
						</a>
						.
					</p>
				</div>
			)
		}
	}

	return (
		<div className="overflow-auto">
			{allNotifs}
		</div>
	);
}

export default function NotificationBar() {
	return (
		<div className="fixed top-0 right-0 mt-4 mr-4 flex flex-initial flex-col bg-white rounded-md shadow-md h-4/6 w-3/12 p-4 overflow-hidden z-10">
			<h1 className="text-center mb-2">Notifications</h1>
			<Notifications />
		</div>
	);
}
