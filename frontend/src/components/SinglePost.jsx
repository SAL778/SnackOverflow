import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getRequest } from "../utils/Requests.jsx";
import PostCard from "./PostCard.jsx";
import CommentCard from "./CommentCard.jsx";
import "./SinglePost.css";

function SinglePost() {
	const { authorId, postId } = useParams();
	const [post, setPost] = useState(null);
	const [isLoading, setIsLoading] = useState(true);
	const [error, setError] = useState(null);
	const [comments, setComments] = useState([]);
	const getPost = () => {
		setIsLoading(true);
		getRequest(`authors/${authorId}/posts/${postId}`)
			.then((data) => {
				console.log("data");
				console.log(data);
				setPost(data);
				let commentUrl = data.comments
				getRequest(commentUrl)
					.then((data) => {
						console.log("data.items")
						console.log(data.items);
						setComments(data.items);
						console.log("comments");
						console.log(comments);
						setIsLoading(false);
					})
					.catch((error) => {
						console.error("Error fetching comments:", error);
						setError(error);
						setIsLoading(false);
					});
			})
			.catch((error) => {
				console.error("Error fetching post:", error);
				setError(error);
				setIsLoading(false);
			});
	}
	useEffect(() => {
		getPost();
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
						postId={post.id.split("/").slice(-1)[0]}
						authorId={post.author.id.split("/").slice(-1)[0]}
						reload={getPost}
					/>
				) : (
					<p>Post not found.</p>
				)}
			</div>
			{
				comments.length > 0 ? (
					<div className="comments-list">
						<div className="comment-card">
							<p>Comments:</p>
						</div>
					{
						comments.map((comment) => {
							const commentDates = new Date(comment.published);
							const formattedCommentDate = `${commentDates.getFullYear()}-${String(
								commentDates.getMonth() + 1
							).padStart(2, "0")}-${String(commentDates.getDate()).padStart(2, "0")}`;
							
							const commentAuthorId = comment.author.id.split("/").slice(-1)[0];
							
							const commentId = comment.id.split("/").slice(-1)[0];
							return (
								<CommentCard
									key={comment.id}
									username={comment.author.displayName}
									date={formattedCommentDate}
									comment={comment.comment}
									authorId={commentAuthorId}
									postId={postId}
									commentId={commentId}
									contentType={comment.contentType}
								/>
							);
						})
					}
				</div>
				) : (
					<div className="no-comment-card">
						<p>No comments yet.</p>
					</div>
					)
			}
		</div>
	);
}

export default SinglePost;
