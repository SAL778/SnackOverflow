import "./NewPost.css";
import React from "react";
import MakePostCard from "./MakePostCard";

const NewPost = () => {
	const handlePostSubmit = (postData) => {
		// Post data to the server
		console.log("Post data to send:", postData);
	};

	const handleCancel = () => {
		// Cancel action: clear the form or redirect to another page
		console.log("Post creation canceled");
	};

	return (
		<div className="new-post-page">
			<MakePostCard onSubmit={handlePostSubmit} onCancel={handleCancel} />
		</div>
	);
};

export default NewPost;
