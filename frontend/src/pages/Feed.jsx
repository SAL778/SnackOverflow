import "./Feed.css";
import React from "react";
import PostCard from "../components/PostCard.jsx";
import { getRequest } from "../utils/Requests.jsx";
import { useAuth } from "../utils/Auth.jsx";
import { useEffect, useState } from "react";
import NotificationBar from "../components/Notifbar.jsx";
import { pollGithub } from "../utils/Github.jsx";

// For the .map() method:
// https://legacy.reactjs.org/docs/lists-and-keys.html

function Feed() {
	const auth = useAuth();
	const [posts, setPosts] = useState([]);

	useEffect(() => {
		//getRequest(`authors/${auth.user.id}/posts`) // current authors posts
		getRequest(`friendsFollowerPosts/`) // posts from friends and followers
			.then((data) => {
				console.log("GET posts Request Data:", data);
				const sortedPosts = data.items.sort(
					(a, b) => new Date(b.published) - new Date(a.published)
				); // Sort the posts by their published date in descending order
				setPosts(sortedPosts);
				setPosts(data.items);
			})
			.catch((error) => {
				console.log("ERROR: ", error.message);
			});
		// start polling if the browser has not done so already
		if (localStorage.getItem("polling") === "false") {
			localStorage.setItem("polling", "true");
			const timeout = 300000;
			// polling will run every 5 minutes until the user logs out
			console.log("polling triggered");
			setTimeout(() => {
				pollGithub(auth.user.github, auth.user.displayName, auth.user.id);
			}, timeout);
		}
	}, []);

	return (
		<div className="feed-container">
			{/* Map over the posts array to display each post */}
			{posts.map((post) => {
				const dates = new Date(post.published); // new Date object based on the post's published date
				const formattedDate = `${dates.getFullYear()}-${String(
					dates.getMonth() + 1
				).padStart(2, "0")}-${String(dates.getDate()).padStart(2, "0")}`;
				// String.padStart(2, "0") is used to ensure the month and day are always two digits long

				const authorId = post.author.id.split("/").slice(-1)[0]; // extract the author's id

				const postId = post.id.split("/").slice(-1)[0]; // extract the post's id

				return (
					<PostCard
						key={post.id}
						username={post.author.displayName}
						title={post.title}
						date={formattedDate}
						description={post.description}
						contentType={post.contentType}
						content={post.content}
						postId={postId}
						sharedBy={post.sharedBy}
						authorId={authorId}
						postVisibility={post.visibility}
					/>
				);
			})}
			{auth.user ? <NotificationBar /> : null}
		</div>
	);
}

export default Feed;
