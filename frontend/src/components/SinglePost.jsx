import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getRequest } from "../utils/Requests.jsx";
import PostCard from "./PostCard.jsx";

function SinglePost() {
	const { authorId, postId } = useParams();
	const [post, setPost] = useState(null);
	const [isLoading, setIsLoading] = useState(true);
	const [error, setError] = useState(null);

	useEffect(() => {
		setIsLoading(true);
		getRequest(`authors/${authorId}/posts/${postId}`)
			.then((data) => {
				setPost(data);
				setIsLoading(false);
			})
			.catch((error) => {
				console.error("Error fetching post:", error);
				setError(error);
				setIsLoading(false);
			});
	}, [authorId, postId]);

	if (isLoading) {
		return <div>Loading...</div>;
	}

	if (error) {
		return <div>Error loading post: {error.message}</div>;
	}

	const dates = new Date(post.published);
	const formattedDate = `${dates.getFullYear()}-${String(
		dates.getMonth() + 1
	).padStart(2, "0")}-${String(dates.getDate()).padStart(2, "0")}`;

	return (
		<div>
			{post ? (
				<PostCard
					key={post.id}
					username={post.author.displayName}
					title={post.title}
					date={formattedDate}
					description={post.description}
					contentType={post.contentType}
					content={post.content}
					imageSrc={post.image}
					postId={post.id}
				/>
			) : (
				<p>Post not found.</p>
			)}
		</div>
	);
}

export default SinglePost;
