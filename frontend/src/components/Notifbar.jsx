import React, { useEffect } from "react";
import Drawer from "@mui/material/Drawer";
import Button from "@mui/material/Button";
import { orange } from "@mui/material/colors";
import { createTheme, ThemeProvider } from "@mui/material/styles";
import { getRequest } from "../utils/Requests.jsx";
import { useAuth } from "../utils/Auth.jsx";
import { Link } from "react-router-dom";
import { extractUUID } from "../utils/Auth.jsx";

const followType = "follow";
const commentType = "comment";
const likeType = "like";

const theme = createTheme({
	palette: {
		primary: orange,
	},
});

function Notifications() {
	// const authorId = post.author.id.split("/").slice(-1)[0]; // extract the author's id

	// const postId = post.id.split("/").slice(-1)[0]; // extract the post's id

	const auth = useAuth();
	const [notifs, setNotifs] = React.useState(null);

	// update page with any notifications that are in the inbox
	useEffect(() => {
		getRequest(`authors/${auth.user.id}/inbox`)
			.then((data) => {
				// console.log('GET inbox data:', data);
				setNotifs(data);
			})
			.catch((error) => {
				console.log("ERROR: ", error.message);
			});
	}, []);
	console.log("here is the notifs");
	console.log(notifs);

	var allNotifs = [];
	// check if notifications have been successfully retrieved and that there are notifications
	// then build the notifications based on that content
	if (notifs && notifs.items.length > 0) {
		var inbox = notifs.items;
		// building the feed for all the objects in the inbox
		for (let object of inbox) {
			const keyIndex = inbox.indexOf(object);
			if (object.type.toLowerCase() === followType) {
				var author = object.actor;
				var authorId = extractUUID(author.url);
				allNotifs.push(
					// TODO: these a elements need to be changed to Link elements
					<div
						key={keyIndex}
						className="flex flex-initial rounded-md shadow-md bg-orange-300/75 p-3 m-2"
					>
						<p className="text-sm">
							<Link
								to={`/profile/${authorId}`}
								className="font-semibold hover:underline hover:text-orange-700"
							>
								{author.displayName}
							</Link>{" "}
							wants to follow you.
						</p>
					</div>
				);
			} else if (object.type === likeType) {
				var author = object.author;
				var authorId = extractUUID(author.url);
				allNotifs.push(
					<div
						key={keyIndex}
						className="flex flex-initial rounded-md shadow-md bg-orange-300/75 p-3 m-2"
					>
						<p className="text-sm">
							<Link
								to={`/profile/${authorId}`}
								className="font-semibold hover:underline hover:text-orange-700"
							>
								{author.displayName}
							</Link>{" "}
							left a like on your{" "}
							<Link
								href={object.object}
								className="font-semibold hover:underline hover:text-orange-700"
							>
								post
							</Link>
							.
						</p>
					</div>
				);
			} else if (object.type === commentType) {
				var author = object.author;
				var authorId = extractUUID(author.url);
				allNotifs.push(
					<div
						key={keyIndex}
						className="flex flex-initial rounded-md shadow-md bg-orange-300/75 p-3 m-2"
					>
						<p className="text-sm">
							<Link
								to={`/profile/${authorId}`}
								className="font-semibold hover:underline hover:text-orange-700"
							>
								{author.displayName}
							</Link>{" "}
							left a comment on your{" "}
							<Link
								href={object.id}
								className="font-semibold hover:underline hover:text-orange-700"
							>
								post
							</Link>
							.
						</p>
					</div>
				);
			}
		}
	} else {
		allNotifs.push(
			<div
				key="1"
				className="flex flex-initial rounded-md shadow-md bg-gray-300/75 p-3 m-2 items-center justify-center"
			>
				<p className="text-sm">No Notifications.</p>
			</div>
		);
	}

	return <div className="overflow-auto">{allNotifs}</div>;
}

export default function NotificationBar() {
	const [open, setOpen] = React.useState(false);

	const toggleDrawer = (newOpen) => () => {
		setOpen(newOpen);
	};

	return (
		<ThemeProvider theme={theme}>
			<div className="fixed top-0 right-0 mt-4 mr-4 bg-white">
				<Button color="primary" onClick={toggleDrawer(true)}>
					Notifications
				</Button>
				<Drawer
					open={open}
					anchor="right"
					onClose={toggleDrawer(false)}
					PaperProps={{
						style: {
							minWidth: "250px",
							width: "auto",
						},
					}}
				>
					<Notifications />
				</Drawer>
			</div>
		</ThemeProvider>
	);
}
