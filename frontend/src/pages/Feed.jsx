import "./Feed.css";
import React from "react";
import PostCard from "../components/PostCard.jsx";
// import temp_image1 from "../assets/snack-logo.png";
// import temp_image2 from "../assets/snoop.jpg";
import { getRequest } from "../utils/Requests.jsx";
import { useAuth } from "../utils/Auth.jsx";
import { useEffect, useState } from "react";
import NotificationBar from "../components/Notifbar.jsx";

function Feed() {
	const auth = useAuth();
	const [posts, setPosts] = useState([]);

	useEffect(() => {
		getRequest(`authors/${auth.userId}/posts`) // post id is not being used?
			.then((data) => {
				console.log("GET posts Request Data:", data);
				const sortedPosts = data.items.sort(
					(a, b) => new Date(b.published) - new Date(a.published)
				);
				setPosts(sortedPosts);
			})
			.catch((error) => {
				console.log("ERROR: ", error.message);
			});
	}, []);

	return (
		<div className="feed-container">
			{posts.map((post) => {
				const dates = new Date(post.published);
				const formattedDate = `${dates.getFullYear()}-${String(
					dates.getMonth() + 1
				).padStart(2, "0")}-${String(dates.getDate()).padStart(2, "0")}`;

				return (
					<PostCard
						key={post.id}
						username={post.author.displayName}
						title={post.title}
						date={formattedDate}
						content={post.content}
					/>
				);
			})}
			{auth.user ? <NotificationBar /> : null}
		</div>
	);
}

export default Feed;
