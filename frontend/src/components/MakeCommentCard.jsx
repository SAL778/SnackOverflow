import React, {useState} from "react";
import Alert from "@mui/material/Alert";
import "./MakeCommentCard.css";

const MakeCommentCard = ({onSubmit, onCancel}) => {
    const [comment, setComment] = useState(""); // State for storing the comment input value
    const [showValidationError, setShowValidationError] = useState(false); // State for showing/hiding validation error message

    // Function to handle the form submission
    const handleSubmit = (event) => {
        event.preventDefault();
        console.log("Submitting comment...");
        // Validate required fields
        if (!comment.trim()) {
            console.log("Fields Missing. Please Check Again.");
            setShowValidationError(true);
            setTimeout(() => setShowValidationError(false), 3000); // Hide alert after 3 seconds
            return;
        }

        setShowValidationError(false);

        // Create a commentData object with the input values
        const commentData = {
            comment,
        };
        console.log("Comment Data:", commentData);
        // Call the onSubmit function with the commentData
        onSubmit(commentData);
    };

    // Function to handle the cancel button click event
    const handleCancel = (event) => {
        event.preventDefault();
        // Clear all the fields and reset the states
        onCancel();
        setComment("");
    };

    return (
        <div className="make-comment-card">
            <form onSubmit={handleSubmit}>
                <div className="input-group">
                    {/* need to increase width and height input field */}
                    <textarea
                        value={comment}
                        onChange={(e) => setComment(e.target.value)}
                        placeholder="Enter your comment here..."
                    />
                </div>
                {showValidationError && (
                    <Alert severity="error">Fields Missing. Please Check Again.</Alert>
                )}
                <div className="button-group">
                    <button 
                        type="submit"
                        className="submit-button"
                    >
                        Submit
                    </button>
                    <button 
                        onClick={handleCancel}
                        type="button"
						className="cancel-button"
                    >
                        Cancel
                    </button>
                </div>
            </form>
        </div>
    );
};
export default MakeCommentCard;