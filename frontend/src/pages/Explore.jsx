import "./Explore.css";
import React from "react";
import PostCard from "../components/PostCard.jsx";
import { getRequest } from "../utils/Requests.jsx";
import { useAuth } from "../utils/Auth.jsx";
import { useEffect, useState } from "react";
import NotificationBar from "../components/Notifbar.jsx";

// For the .map() method:
// https://legacy.reactjs.org/docs/lists-and-keys.html

function Explore() {
	const auth = useAuth();
	const [posts, setPosts] = useState([]);

	useEffect(() => {
		getRequest(`publicPosts/`)
			.then((data) => {
				console.log("GET posts Request Data:", data);
				const sortedPosts = data.items.sort(
					(a, b) => new Date(b.published) - new Date(a.published)
				); // Sort the posts by their published date in descending order
				setPosts(sortedPosts);
			})
			.catch((error) => {
				console.log("ERROR: ", error.message);
			});
	}, []);

	return (
		<div className="explore-container">
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
						authorId={authorId}
						postVisibility={post.visibility}
					/>
				);
			})}
			{auth.user ? <NotificationBar /> : null}
		</div>
	);
}

export default Explore;
