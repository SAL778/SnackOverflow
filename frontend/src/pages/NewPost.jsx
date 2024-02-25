import "./NewPost.css";
import React from "react";
import MakePostCard from "../components/MakePostCard";
import { getRequest, postRequest } from "../utils/Requests.jsx";
import { useAuth } from "../utils/Auth.jsx";
// import { useEffect, useState } from "react";

const NewPost = () => {
	const auth = useAuth();

	const handlePostSubmit = async (postData) => {
		const dataToSend = {
			title: postData.title,
			description: postData.title,
			contentType: postData.isMarkdown ? "text/markdown" : "text/plain",
			content: postData.content,
			visibility: postData.postType.toUpperCase(),
		};

		try {
			const data = await postRequest(
				`authors/${auth.userId}/posts/`,
				JSON.stringify(dataToSend)
			);
			console.log("POST Request Data:", data);
		} catch (error) {
			console.log("ERROR: ", error);
		}
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
