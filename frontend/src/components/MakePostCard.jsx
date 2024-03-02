// Component for creating a post card
// It allows users to input a title, select a post type, add a description, choose between plain text or markdown content,
// upload media files, and submit or cancel the post.
import "./MakePostCard.css";
import Alert from "@mui/material/Alert";
import React, { useState } from "react";
const MakePostCard = ({ onSubmit, onCancel }) => {
	const [title, setTitle] = useState(""); // State for storing the title input value
	const [postType, setPostType] = useState(""); // State for storing the selected post type
	const [content, setContent] = useState(""); // State for storing the content input value
	const [description, setDescription] = useState(""); // State for storing the description input value
	const [isMarkdown, setIsMarkdown] = useState(false); // State for tracking if the content is in markdown format
	const [images, setImages] = useState([]); // State for storing the uploaded image files
	const [showValidationError, setShowValidationError] = useState(false); // State for showing/hiding validation error message

	// Function to handle the click event on post type buttons
	const handlePostTypeClick = (type) => {
		setPostType(type);
	};

	// Function to handle the file upload event for images
	const handleImageUpload = (event) => {
		setImages([...event.target.files]);
	};

	// Function to handle the form submission
	const handleSubmit = (event) => {
		event.preventDefault();

		// Validate required fields
		if (!title.trim() || !content.trim() || !postType.trim()) {
			setShowValidationError(true);
			setTimeout(() => setShowValidationError(false), 3000); // Hide alert after 3 seconds
			return;
		}

		setShowValidationError(false);

		// Create a postData object with the input values
		const postData = {
			title,
			postType,
			description,
			content,
			isMarkdown,
			images,
		};

		// Call the onSubmit function with the postData
		onSubmit(postData);
	};

	// Function to handle the cancel button click event
	const handleCancel = (event) => {
		event.preventDefault();
		// Clear all the fields and reset the states
		onCancel();
		setTitle("");
		setContent("");
		setDescription("");
		setImages([]);
		setPostType("");
		setIsMarkdown(false);
	};

	return (
		<div style={{ margin: "0px 0px 50px 200px" }}>
			{/* validation error, fields cannot be empty. */}
			{showValidationError && (
				<Alert severity="error">Fields Missing. Please Check Again.</Alert>
			)}
			<div className="make-post-card">
				{/* Form for creating a new post */}
				<form onSubmit={handleSubmit}>
					{/* Input field for the post title */}
					<div className="form-group">
						<label htmlFor="title">Title:</label>
						<input
							id="title"
							type="text"
							value={title}
							onChange={(e) => setTitle(e.target.value)}
							placeholder="Give your post a title..."
						/>
					</div>
					{/* Buttons for selecting the post type */}
					<div className="form-group">
						<label>Post Type:</label>
						<div
							className="post-type-buttons"
							style={{
								display: "flex",
								justifyContent: "center",
								alignItems: "center",
							}}
						>
							{["Friends", "Public", "Unlisted"].map((type) => (
								<button
									key={type}
									type="button"
									className={postType === type ? "selected" : ""}
									onClick={() => handlePostTypeClick(type)}
								>
									{type.replace("-", " ")}
								</button>
							))}
						</div>
					</div>
					{/* Input field for the post description */}
					<div className="form-group">
						<label htmlFor="description">Description:</label>
						<input
							id="description"
							type="text"
							value={description}
							onChange={(e) => setDescription(e.target.value)}
							placeholder="Summarize your post here..."
						/>
					</div>
					{/* Textarea for the post content */}
					<div className="form-group">
						<label>Content:</label>
						<div
							className="toggle-switch"
							style={{
								display: "flex",
								marginBottom: "20px",
							}}
						>
							<button
								type="button"
								className={!isMarkdown ? "selected" : ""}
								onClick={() => setIsMarkdown(false)}
							>
								Text
							</button>
							<button
								type="button"
								className={isMarkdown ? "selected" : ""}
								onClick={() => setIsMarkdown(true)}
							>
								Markdown
							</button>
						</div>
						<textarea
							value={content}
							onChange={(e) => setContent(e.target.value)}
							placeholder="Post content goes here..."
						/>
					</div>
					{/* Input for uploading media. Comes into effect later, Project Part 2 */}
					<div className="form-group">
						<label>Media:</label>
						<input type="file" multiple onChange={handleImageUpload} />
					</div>
					{/* Buttons for canceling or submitting the form */}
					<div className="form-actions">
						<button
							type="button"
							className="cancel-button"
							onClick={handleCancel}
						>
							Cancel
						</button>
						<button
							type="submit"
							className="submit-button"
							onClick={handleSubmit}
						>
							Post
						</button>
					</div>
				</form>
			</div>
		</div>
	);
};

export default MakePostCard;
