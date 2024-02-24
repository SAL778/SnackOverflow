import "./MakePostCard.css";
import React, { useState } from "react";

const MakePostCard = ({ onSubmit, onCancel }) => {
	const [title, setTitle] = useState("");
	const [postType, setPostType] = useState("");
	const [content, setContent] = useState("");
	const [isMarkdown, setIsMarkdown] = useState(false);
	const [images, setImages] = useState([]);

	const handlePostTypeClick = (type) => {
		setPostType(type);
	};

	const handleImageUpload = (event) => {
		setImages([...event.target.files]);
	};

	const handleSubmit = (event) => {
		event.preventDefault();

		//postData object
		const postData = {
			title, // the title of the post, sent as a string
			postType, // Friends, Public, Unlisted
			content, // the content of the post, sent as a string (for both, markdown and plain text)
			isMarkdown, // true if the content is in markdown format
			images, // an array of image files to be uploaded with the post (if any)
		};

		onSubmit(postData);
	};
	const handleCancel = (event) => {
		event.preventDefault();
		onCancel();
		setTitle(""); // Clear the fields
		setContent(""); // Clear the fields
	};

	return (
		<div style={{ margin: "0px 0px 50px 200px" }}>
			<div className="make-post-card">
				<form onSubmit={handleSubmit}>
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
					<div className="form-group">
						<label>content:</label>
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
					<div className="form-group">
						<label>Media:</label>
						<input type="file" multiple onChange={handleImageUpload} />
					</div>
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
