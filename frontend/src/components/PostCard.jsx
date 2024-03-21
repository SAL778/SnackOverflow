import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { deleteRequest, postRequest, getRequest } from "../utils/Requests.jsx";
import { useAuth } from "../utils/Auth.jsx";
import { Pencil, Trash } from "@phosphor-icons/react";
import ReactMarkdown from "react-markdown";
import "./PostCard.css";
import Alert from "@mui/material/Alert";
import MakeCommentCard from "./MakeCommentCard.jsx";
import { useNavigate } from "react-router-dom";

function PostCard({
	username,
	title,
	date,
	description,
	contentType,
	content,
	profilePage,
	setAuthPosts,
	authPosts,
	postId,
	sharedBy = "",
	authorId,
	postVisibility,
	reload,
	owner,
}) {
	const [likes, setLikes] = useState(0); // DUMMY LIKE DATA
	const auth = useAuth();
	const [showDeleteAlert, setShowDeleteAlert] = useState(false); // State to control alert visibility
	const [likesObjet, setLikesObject] = useState([]); // State to store the likes for the post
	const [clickedComment, setClickedComment] = useState(false); // State to control comment visibility
	const serviceUrl = window.location.protocol + "//" + window.location.host;
	const navigate = useNavigate();

	const handleLike = () => {
		// check if the user has already liked the post
		let alreadyLiked = false;
		likesObjet.forEach((like) => {
			var likedAuthorId = like.author.id.split("/").pop();
			if (likedAuthorId === auth.user.id) {
				alreadyLiked = true;
			}
			if (alreadyLiked) {
				console.log("You have already liked this post");
				return;
			}
		});
		if (!alreadyLiked) {
			// if not, post a like request
			console.log(auth.user.displayName, " liked the post-", auth.user.id);

			let dataToSend = {
				type: "inbox",
				// this is the author of the post
				author: `${serviceUrl}/authors/${authorId}`,
				items: [
					{
						type: "Like",
						summary: `${auth.user.displayName} liked your post`,
						// this is the author of the like
						author: {
							id: `${serviceUrl}/authors/${auth.user.id}`,
						},
						object: `${serviceUrl}/authors/${authorId}/posts/${postId}`,
					},
				],
			};

			postRequest(`authors/${authorId}/inbox`, dataToSend, false)
				.then((response) => {
					console.log("Like posted successfully");
					console.log(response);
					getLikes();
				})
				.catch((error) => {
					console.error("Error posting the like: ", error.message);
				});
		}
	};

	const getLikes = () => {
		// get the likes for the post from doing a get request
		getRequest(`authors/${authorId}/posts/${postId}/likes`)
			.then((response) => {
				console.log("Likes: ", response);
				setLikes(response.items.length);
				setLikesObject(response.items);
			})
			.catch((error) => {
				console.error("Error getting likes: ", error.message);
			});
	};

	const handleDelete = () => {
		deleteRequest(`authors/${authorId}/posts/${postId}`) // why is it this url? It works but I don't know why figure it out
			.then((response) => {
				console.log("Post deleted successfully");
				setShowDeleteAlert(true); // Show "Post Deleted" alert
				setTimeout(() => setShowDeleteAlert(false), 3000); // Hide alert after 3 seconds
				if (!setAuthPosts) {
					// this is done from the posts individual page so redirect to profile page
					return;
				}
				var newAuthPosts = authPosts.filter((post) => post.id !== postId);
				setAuthPosts(newAuthPosts);
			})
			.catch((error) => {
				console.error("Error deleting the post: ", error.message);
			});
	};

	const handleShare = () => {
		//authors/<uuid:id_author>/posts/<uuid:id_post>
		//get the post, get data and visibility from it
		let name = "";
		console.log(auth);
		console.log("CHECK ID: ", postId);
		getRequest(`authors/${authorId}/posts/${postId}`).then((data) => {
			console.log("Getting post: ", data);
			name = data.author.displayName;
		});
		/*
		const dataToSend = {
			title: title,
			username: name,
			description: description,
			contentType: contentType,
			content: content,
			visibility: "PUBLIC",
			sharedBy: auth.user.displayName
		}
		*/

		const dataToSend = new FormData();

		dataToSend.append("title", title);
		dataToSend.append("description", description);
		dataToSend.append("contentType", contentType);
		dataToSend.append("content", content);
		dataToSend.append("visibility", "PUBLIC");
		dataToSend.append("sharedBy", auth.user.displayName);

		//console.log("TEST SHAREDBY: ", dataToSend.sharedBy)
		postRequest(`authors/${auth.user.id}/posts/`, dataToSend, false)
			.then((data) => {
				console.log("SHARED POST POSTED");
			})
			.catch((error) => {
				console.log("ERROR: ", error.message);
			});
	};

	const handleComment = () => {
		setClickedComment(true);
	};

	const handleCommentSubmit = async (commentData) => {
		if (!commentData.comment) {
			return;
		}
		let dataToSend = {
			type: "inbox",
			author: `${serviceUrl}/authors/${authorId}`,
			items: [
				{
					type: "Comment",
					author: {
						id: `${serviceUrl}/authors/${auth.user.id}`,
					},
					comment: commentData.comment,
					contentType: "text/markdown",
					post: {
						id: `${serviceUrl}/authors/${authorId}/posts/${postId}}`,
					},
				},
			],
		};
		try {
			// post the comment request
			postRequest(`authors/${authorId}/inbox`, dataToSend, false)
				.then((response) => {
					console.log("Comment posted successfully");
					console.log(response);
					setClickedComment(false);
					if (reload) {
						reload();
					}
				})
				.catch((error) => {
					console.error("Error posting the comment: ", error.message);
				});
		} catch (error) {
			console.log("ERROR: ", error);
		}
	};

	const [showCommentSuccess, setShowCommentSuccess] = useState(false);

	const handleCommentSubmitWrapper = async (commentData) => {
		await handleCommentSubmit(commentData); // Call the existing submit function
		setShowCommentSuccess(true); // Show the alert at the PostCard level
		setTimeout(() => setShowCommentSuccess(false), 3000); // Hide the alert after 3 seconds
	};

	const handleCommentCancel = () => {
		setClickedComment(false);
		console.log("Comment creation canceled");
	};

	useEffect(() => {
		console.log("PostCard useEffect");
		getLikes();
	}, []);

	// debugging console log. Print the base64 image source
	useEffect(() => {
		console.log("Base64 Image Source:", content);
	}, [content]);

	return (
		<div className={profilePage ? "post-card-profile-page" : "post-card"}>
			{showCommentSuccess && (
				<Alert
					severity="success"
					style={{
						position: "fixed",
						zIndex: 2,
						bottom: 40,
						right: 40,
					}}
				>
					Comment Added
				</Alert>
			)}
			{showDeleteAlert && (
				<Alert
					severity="success"
					style={{
						position: "absolute",
						zIndex: 2,
						width: "200px",
						height: "200px",
						marginBottom: "200px",
						marginLeft: "200px",
						display: "flex",
						flexDirection: "column",
						justifyContent: "center",
						alignItems: "center",
					}}
				>
					Post Deleted
				</Alert>
			)}
			{profilePage && owner && (
				<div className="post-edit-delete">
					<div className="post-edit-delete">
						<button
							onClick={() => navigate(`/edit-post/${authorId}/${postId}`)}
							style={{ marginRight: "10px" }}
							className="edit-button"
						>
							<Pencil size={32} />
						</button>
					</div>
					<button onClick={handleDelete}>
						<Trash size={32} color="red" />
					</button>
				</div>
			)}

			{!profilePage && sharedBy === "" && (
				<Link to={`/profile/${authorId}`} className="username">
					User: {username}
				</Link>
			)}

			{!(sharedBy === "") && (
				<a href="/profile" className="username">
					Shared By: {sharedBy}
				</a>
			)}

			{postVisibility === "UNLISTED" && (
				<p>Link: {`${serviceUrl}/profile/${authorId}/posts/${postId}`} </p>
			)}
			{/* <h1 className="post-header">{title}</h1> */}
			<h1 className="post-header">
				<Link to={`/profile/${authorId}/posts/${postId}`}>{title}</Link>
			</h1>

			<span className="post-date">Date: {date}</span>
			<p className="post-description">
				Description:
				<br />
				{description}
			</p>
			{/* Check the content type and show accordingly */}
			{content && (
				<div className="post-content">
					{contentType === "text/markdown" ? (
						<ReactMarkdown>{content}</ReactMarkdown>
					) : contentType === "text/plain" ? (
						<p>{content}</p>
					) : (
						<img
							src={content}
							alt="Post"
							onError={(e) => {
								console.log("Error loading image");
								e.target.style.display = "none";
							}}
						/>
					)}
				</div>
			)}
			<div className="post-footer">
				<button className="interactive-button" onClick={handleLike}>
					Likes: {likes} 👍
				</button>

				<div style={{ display: "flex", justifyContent: "space-between" }}>
					{postVisibility === "PUBLIC" && (
						<button
							className="interactive-button"
							style={{ marginRight: "10px" }}
							onClick={handleShare}
						>
							Share
						</button>
					)}
					<button className="interactive-button" onClick={handleComment}>
						Comment
					</button>
				</div>
			</div>
			{clickedComment && (
				<div className="new-comment-card">
					<MakeCommentCard
						onSubmit={handleCommentSubmitWrapper}
						onCancel={handleCommentCancel}
					/>
				</div>
			)}
		</div>
	);
}

export default PostCard;

// from ChatGPT: rendering markdown in react:
// prompt: "How do I render markdown content in React? Steps to use the markdown correctly instead of treating it as text."  5:15 a.m. 22/02/2024

// import marked from 'marked'; // Assuming you're using the 'marked' library
// Note: import commonmark from 'commonmark'; // If you're using 'commonmark' library as well

// const renderPostDescription = (post) => {
//   if (post.isMarkdown) {
//     const rawMarkup = marked(post.description);
//     return <div dangerouslySetInnerHTML={{ __html: rawMarkup }} />;
//   } else {
//     return <div>{post.description}</div>;
//   }
// };

// import { Parser } from "commonmark";
// const parser = new Parser();
// const [renderedContent, setRenderedContent] = useState("");

// Backend Storage: Store the description and the format (Markdown or plain text) in your database.

// Rendering Posts: When rendering posts, check the format. If a post's description is in Markdown, you'll use a Markdown renderer to convert the Markdown to HTML on-the-fly before displaying it. If it's plain text, you'll display it as is.

// Markdown Library: When it comes to displaying the posts with Markdown content, you'll need a Markdown rendering library to convert the Markdown to HTML. Libraries like marked or remarkable are popular choices for this.

// Note: dangerouslySetInnerHTML is React's way of inserting HTML into the DOM, and as the name implies, it's dangerous because it can open you up to XSS attacks if the content isn't sanitized.
// Security: Sanitize the output of the Markdown renderer to prevent XSS attacks. Libraries like DOMPurify can sanitize HTML content.
