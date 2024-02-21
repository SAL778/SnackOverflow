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
