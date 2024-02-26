import React, { useState } from "react";
import { Link } from "react-router-dom"; //can be used later to link to the user's profile, replace <a> with <Link>
import { deleteRequest } from "../utils/Requests.jsx";
import { useAuth } from "../utils/Auth.jsx";
import { Pencil, Trash } from "@phosphor-icons/react";
import ReactMarkdown from "react-markdown";
import "./PostCard.css";
import Alert from "@mui/material/Alert";

function PostCard({
	username,
	title,
	date,
	imageSrc,
	description,
	contentType,
	content,
	profilePage,
	setAuthPosts,
	authPosts,
	postId,
}) {
	const [likes, setLikes] = useState(0); // DUMMY DATA
	const auth = useAuth();
	const [showDeleteAlert, setShowDeleteAlert] = useState(false); // State to control alert visibility

	const handleLike = () => {
		setLikes((prevLikes) => prevLikes + 1);
	};
	const handleDelete = () => {
		deleteRequest(`${postId}`) // why is it this url? It works but I don't know why figure it out
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
	const handleEdit = () => {
		// redirect to the edit post page
		console.log("Edit post");
	};

	return (
		<div className={profilePage ? "post-card-profile-page" : "post-card"}>
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
			{profilePage && (
				<div className="post-edit-delete">
					<button onClick={handleEdit} style={{ marginRight: "10px" }}>
						<Pencil size={32} />
					</button>
					<button onClick={handleDelete}>
						<Trash size={32} color="red" />
					</button>
				</div>
			)}
			{!profilePage && (
				<a href="/profile" className="username">
					User: {username}
				</a>
			)}

			<h1 className="post-header">{title}</h1>
			<span className="post-date">Date: {date}</span>
			{imageSrc && <img src={imageSrc} alt="Post" />}
			<p className="post-description">
				Description:
				<br />
				{description}
			</p>
			<div className="post-content">
				{contentType === "text/markdown" ? (
					<ReactMarkdown>{content}</ReactMarkdown>
				) : (
					<p>{content}</p>
				)}
			</div>
			<div className="post-footer">
				<button onClick={handleLike}>Likes: {likes} 👍</button>
				<div>
					<button>Share</button>
					<button>Comment</button>
				</div>
			</div>
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
