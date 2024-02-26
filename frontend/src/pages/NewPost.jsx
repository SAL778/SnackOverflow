import "./NewPost.css";
import React from "react";
import MakePostCard from "../components/MakePostCard";
import { postRequest } from "../utils/Requests.jsx";
import { useAuth } from "../utils/Auth.jsx";
import Alert from "@mui/material/Alert";
import { useState } from "react";

const NewPost = () => {
	const auth = useAuth();
	const [showSuccessAlert, setShowSuccessAlert] = useState(false);

	const handlePostSubmit = async (postData) => {
		if (!postData.title || !postData.content || !postData.postType) {
			return;
		}

		const dataToSend = {
			title: postData.title,
			description: postData.description,
			contentType: postData.isMarkdown ? "text/markdown" : "text/plain",
			content: postData.content,
			visibility: postData.postType.toUpperCase(),
		};

		try {
			const data = await postRequest(
				`authors/${auth.userId}/posts/`,
				//JSON.stringify(dataToSend)
				dataToSend
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
			<MakePostCard onSubmit={handlePostSubmit} onCancel={handleCancel} />
		</div>
	);
};

export default NewPost;
