import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom"; //can be used later to link to the user's profile, replace <a> with <Link>
import { deleteRequest, getRequest, postRequest } from "../utils/Requests.jsx";
import { useAuth } from "../utils/Auth.jsx";
import { Pencil, Trash } from "@phosphor-icons/react";
import ReactMarkdown from "react-markdown";
import "./PostCard.css";
import Alert from "@mui/material/Alert";
import MakeCommentCard from "./MakeCommentCard.jsx";

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
	authorId,
	postVisibility,
}) {
	const [likes, setLikes] = useState(0); // DUMMY LIKE DATA
	const auth = useAuth();
	const [showDeleteAlert, setShowDeleteAlert] = useState(false); // State to control alert visibility
	const [likesObjet, setLikesObject] = useState([]); // State to store the likes for the post
	const [clickedComment, setClickedComment] = useState(false); // State to control comment visibility
	const serviceUrl = "https://socialapp-api.herokuapp.com";
	
	const handleLike = () => {
		// check if the user has already liked the post
		let alreadyLiked = false;
		likesObjet.forEach((like) => {
			var likedAuthorId = like.author.id.split("/").pop();
			if (likedAuthorId === auth.user.id) {
				alreadyLiked = true;
			}
			if (alreadyLiked) {
				console.log("You have already liked this post");
				return;
			}
		});
		if (!alreadyLiked) {
			// if not, post a like request
			//TODO: post the like request
			console.log(auth.user.displayName, " liked the post-" , auth.user.id);

			let dataToSend = {
				"type":"inbox",
				// this is the author of the post
				"author":`${serviceUrl}/authors/${authorId}`,
				"items":[
					{
						"type":"Like",
						"summary":`${auth.user.displayName} liked your post`,
						// this is the author of the like
						"author":{
							id: `${serviceUrl}/authors/${auth.user.id}`,
						},
						object : `${serviceUrl}/authors/${authorId}/posts/${postId}`
					}
				]
			}

			postRequest(`authors/${authorId}/inbox`, dataToSend, false)
				.then((response) => {
					console.log("Like posted successfully");
					console.log(response);
					getLikes();
				})
				.catch((error) => {
					console.error("Error posting the like: ", error.message);
				});	
		}
	};

	const getLikes = () =>{
		// get the likes for the post from doing a get request
		getRequest(`authors/${authorId}/posts/${postId}/likes`)
			.then((response) => {
				console.log("Likes: ", response);
				setLikes(response.items.length);
				setLikesObject(response.items);
			})
			.catch((error) => {
				console.error("Error getting likes: ", error.message);
			});
	}

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
		// redirect to the edit post page later
		console.log("Edit post");
	};

	const handleComment = () => {
		setClickedComment(true);
	}

	const handleCommentSubmit = async (commentData) => {
		if(!commentData.comment){
			return;
		}
		let dataToSend = {
			"type":"inbox",
			"author":`${serviceUrl}/authors/${authorId}`,
			"items":[
				{
					"type":"Comment",
					"author":{
						id: `${serviceUrl}/authors/${auth.user.id}`,
					},
					"comment": commentData.comment,
					"contentType":"text/plain",
					"post":{
						id: `${serviceUrl}/authors/${authorId}/posts/${postId}}`
					}
				}
			]
		}
		try{
			// post the comment request
			postRequest(`authors/${authorId}/inbox`, dataToSend, false)
				.then((response) => {
					console.log("Comment posted successfully");
					console.log(response);
					setClickedComment(false);
				})
				.catch((error) => {
					console.error("Error posting the comment: ", error.message);
				});
		}
		catch (error) {
			console.log("ERROR: ", error);
		}
	}
	
	const handleCommentCancel = () => {
		setClickedComment(false);
		console.log("Comment creation canceled");
	}

	useEffect(() => {
		console.log("PostCard useEffect");
		getLikes();
	}, []);

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
				<Link to={`/profile/${authorId}`} className="username">
					User: {username}
				</Link>
			)}
			{postVisibility === "UNLISTED" && 
				<p>Link: {`${serviceUrl}/profile/${authorId}/posts/${postId}`} </p>
			}
			{/* <h1 className="post-header">{title}</h1> */}
			<h1 className="post-header">
				<Link to={`/profile/${authorId}/posts/${postId}`}>{title}</Link>
			</h1>
			<span className="post-date">Date: {date}</span>
			{imageSrc && <img src={imageSrc} alt="Post" />}
			<p className="post-description">
				Description:
				<br />
				{description}
			</p>
			{content &&
				(
					<div className="post-content">
						{contentType === "text/markdown" ? (
							<ReactMarkdown>{content}</ReactMarkdown>
						) : (
							<p>{content}</p>
						)}
					</div>
				)
			}
			<div className="post-footer">
				<button onClick={handleLike}>Likes: {likes} 👍</button>
				<div>
					<button>Share</button>
					<button onClick={handleComment}>Comment</button>
				</div>
			</div>
			{clickedComment && (
				<div className="new-comment-card">
					<MakeCommentCard onSubmit={handleCommentSubmit} onCancel={handleCommentCancel} />
				</div>
			)}
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
