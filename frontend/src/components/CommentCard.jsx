import { useAuth } from "../utils/Auth";
import "./CommentCard.css";
import ReactMarkdown from "react-markdown";

function CommentCard({
	username,
	date,
	contentType,
	comment,
	authorId,
	postId,
	commentId,
}) {
	const auth = useAuth();
	const serviceUrl = "https://socialapp-api.herokuapp.com";

	return (
		<div className="comment-card">
			<div className="comment-card-header">
				<div className="comment-card-username">{username}</div>
				<div className="comment-card-date">Date: {date}</div>
			</div>
			<div className="comment-card-content">
				{contentType === "text/markdown" ? (
					<ReactMarkdown>{comment}</ReactMarkdown>
				) : (
					<p>{comment}</p>
				)}
			</div>
		</div>
	);
}
export default CommentCard;
