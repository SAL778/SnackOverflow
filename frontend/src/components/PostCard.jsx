import React, { useState } from "react";
import { Link } from "react-router-dom"; //can be used later to link to the user's profile, replace <a> with <Link>
import "./PostCard.css";

function PostCard({ username, title, date, imageSrc, description }) {
	const [likes, setLikes] = useState(420); // DUMMY DATA

	const handleLike = () => {
		setLikes((prevLikes) => prevLikes + 1);
	};

	return (
		<div className="post-card">
			<a href="/profile" className="username">
				{username}
			</a>
			<h1 className="post-header">{title}</h1>
			<span className="post-date">{date}</span>
			{imageSrc && <img src={imageSrc} alt="Post" />}
			<div className="post-description">
				<p>{description}</p>
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
