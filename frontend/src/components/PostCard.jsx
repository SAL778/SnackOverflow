import React, { useState } from "react";
import { Link } from "react-router-dom"; //can be used later to link to the user's profile, replace <a> with <Link>
import { deleteRequest } from "../utils/Requests.jsx";
import { useAuth } from "../utils/Auth.jsx";
import { Pen, Trash } from "@phosphor-icons/react";
import "./PostCard.css";

function PostCard({ username, title, date, imageSrc, content, profilePage, setAuthPosts, authPosts, postId}) {
	const [likes, setLikes] = useState(0); // DUMMY DATA
	const auth = useAuth();
	
	const handleLike = () => {
		setLikes((prevLikes) => prevLikes + 1);
	};
	const handleDelete = () => {
		deleteRequest(`${postId}`) // why is it this url? It works but I don't know why figure it out
			.then((response) => {
				console.log("Post deleted successfully");
				if (!setAuthPosts) {
					// this is done from the posts individual page so redirect to profile page
					return
				};
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
		<div className={profilePage? "post-card-profile-page":"post-card"}>
			{profilePage && 
				<div className="post-edit-delete">
					<button onClick={handleEdit}><Pen size={32}/></button>
					<button onClick={handleDelete}><Trash size={32}/></button>
				</div>
			}
			{ !profilePage &&
				<a href="/profile" className="username">
					User: {username}
				</a>
			}

			<h1 className="post-header">{title}</h1>
			<span className="post-date">Date: {date}</span>
			{imageSrc && <img src={imageSrc} alt="Post" />}
			<div className="post-content">
				<p>{content}</p>
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

// from ChatGPT: rendering markdown as html in react:
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
