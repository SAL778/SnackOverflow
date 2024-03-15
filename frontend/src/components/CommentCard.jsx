import React, {useState, useEffect} from "react";
import { getRequest, postRequest } from "../utils/Requests";
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
}){
    const auth = useAuth();
    const [likes, setLikes] = useState(0);
    const [likesObject, setLikesObject] = useState([]);
    const serviceUrl = "https://socialapp-api.herokuapp.com";
    //TODO: like doesn't work fix that
    const handleLike = () => {
        let alreadyLiked = false;
        likesObject.forEach((like) => {
            var likedAuthorId = like.author.id.split("/").pop();
            if (likedAuthorId === auth.user.id) {
                alreadyLiked = true;
            }
            if (alreadyLiked) {
                console.log("You have already liked this comment");
                return;
            }
        });
        if(!alreadyLiked){
            // if not post a like request
            console.log(auth.user.displayName, " liked the comment-", auth.user.id);
            //TODO: post a like request
            let dataToSend = {
                "type":"inbox",
                "author":`${serviceUrl}/authors/${authorId}`,
                "items":[
                    {
                        "type":"Like",
                        "summary":`${auth.user.displayName} liked your comment`,
                        "author":{
                            id: `${serviceUrl}/authors/${auth.user.id}`,
                        },
                        object : `${serviceUrl}/authors/${authorId}/posts/${postId}/comments/${commentId}`
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
        getRequest(`authors/${authorId}/posts/${postId}/comments/${commentId}/likes`)
            .then((response) => {
                console.log("Likes: ", response);
                setLikes(response.items.length);
                setLikesObject(response.items);
            })
            .catch((error) => {
                console.error("Error getting likes: ", error.message);
            });
    }

    useEffect(() => {
        console.log("Getting comment likes");
        getLikes();
    }, []);

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
            <div className="comment-card-likes">
                <button onClick={handleLike}>Likes: {likes} 👍</button>
            </div>
        </div>
    )
}
export default CommentCard;