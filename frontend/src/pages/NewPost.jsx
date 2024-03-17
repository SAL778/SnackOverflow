import "./NewPost.css";
import React from "react";
import MakePostCard from "../components/MakePostCard";
import { postRequest, putRequest, getRequest } from "../utils/Requests.jsx";
import { useAuth } from "../utils/Auth.jsx";
import Alert from "@mui/material/Alert";
import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";

const NewPost = ({ editMode }) => {
	const { authorId, postId } = useParams();
	const [initialPostData, setInitialPostData] = useState(null);
	const auth = useAuth();
	const [showSuccessAlert, setShowSuccessAlert] = useState(false);

	useEffect(() => {
		if (editMode) {
			// Fetch the post data and set it as initial data
			getRequest(`authors/${authorId}/posts/${postId}`)
				.then((data) => setInitialPostData(data))
				.catch((error) => console.error("Fetch error:", error));
		}
	}, [editMode, authorId, postId]);

	const handlePostSubmit = async (postData) => {
		if (!postData.title || !postData.postType) {
			return;
		}
		let contentType = "text/plain";
		if (postData.isMarkdown) {
			contentType = "text/markdown";
		} else if (postData.isImage) {
			contentType = "image/png;base64";
		}
		const dataToSend = new FormData();
		dataToSend.append("title", postData.title);
		dataToSend.append("description", postData.description);
		dataToSend.append("contentType", contentType);
		dataToSend.append("visibility", postData.postType.toUpperCase());
		if (!postData.isImage && postData.content) {
			dataToSend.append("content", postData.content);
		}
		if (postData.isImage && postData.image) {
			dataToSend.append("image", postData.image, postData.image.name); // Only one image for now (to be updated later)
		}
		// console.log("Data to send:", dataToSend);

		try {
			const data = await postRequest(
				`authors/${auth.user.id}/posts/`,
				//JSON.stringify(dataToSend)
				dataToSend,
				true
			);
			console.log("POST Request Data:", data);
			setShowSuccessAlert(true);
			setTimeout(() => setShowSuccessAlert(false), 3000); // Hide alert after 3 seconds
		} catch (error) {
			console.log("ERROR: ", error);
		}
	};

	const handleCancel = () => {
		// Cancel action: clear the form or redirect to another page, clear for now.
		console.log("Post creation canceled");
	};

	return (
		<div className="new-post-page">
			{showSuccessAlert && (
				<Alert
					severity="success"
					style={{
						position: "absolute",
						zIndex: 2,
						width: "400px",
						height: "400px",
						marginBottom: "200px",
						marginLeft: "200px",
						display: "flex",
						flexDirection: "column",
						justifyContent: "center",
						alignItems: "center",
					}}
				>
					Post Successful
				</Alert>
			)}
			<MakePostCard
				onSubmit={handlePostSubmit}
				onCancel={handleCancel}
				initialData={initialPostData}
				authorId={authorId}
				postId={postId}
			/>
		</div>
	);
};

export default NewPost;
