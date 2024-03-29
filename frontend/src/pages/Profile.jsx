import React, { useEffect, useState } from "react";
import ProfileCard from "../components/ProfileCard.jsx";
import PostCard from "../components/PostCard.jsx";
import { getRequest, postRequest } from "../utils/Requests.jsx";
import { useAuth } from "../utils/Auth.jsx";
import { useParams } from "react-router-dom";
import Alert from "@mui/material/Alert";

//Buttons modified from this source: https://flowbite.com/docs/components/button-group/ Accessed Feb 10th
function Profile() {
	const { source } = useParams();
	const auth = useAuth();

	const [authProfile, setAuthProfile] = useState([]);
	const [followers, setFollowers] = useState([]);
	const [followings, setFollowings] = useState([]);
	const [friends, setFriends] = useState([]);
	const [authPosts, setAuthPosts] = useState([]);
	const [authFollowReqs, setAuthFollowReqs] = useState([]);

	const [showFollowers, setShowFollowers] = useState(false);
	const [showFollowing, setShowFollowing] = useState(false);
	const [showFriends, setShowFriends] = useState(false);
	const [showPosts, setShowPosts] = useState(false);
	const [showReqs, setShowReqs] = useState(false);

	const buttons = [
		{ name: "Followers", stateSetter: setShowFollowers },
		{ name: "Following", stateSetter: setShowFollowing },
		{ name: "Friends", stateSetter: setShowFriends },
		{ name: "Posts", stateSetter: setShowPosts },
		{ name: "Follow Requests", stateSetter: setShowReqs },
	];

	const [changeProfile, setChangeProfile] = useState(false);
	const flipChangeProfile = (change) => {
		setChangeProfile(!change);
	};

	let profileUUID = auth.user.id;
	let owner = true;

	if (source === undefined) {
		//console.log("No source, portay profile as logged-in user");
		profileUUID = auth.user.id; //redundant but explicit
		owner = true; //redundant but explicit
	} else if (source === profileUUID) {
		//console.log("Accessing Own Profile.");
		profileUUID = auth.user.id; //redundant but explicit
		owner = true; //redundant but explicit
	} else {
		//ASSUMING THAT THE SOURCE IS VALID
		profileUUID = source;
		owner = false;
	}

	useEffect(() => {
		getRequest(`authors/${profileUUID}`)
			.then((data) => {
				console.log("GET author Request Data:", data);
				setAuthProfile(data);
			})
			.catch((error) => {
				console.log("ERROR: ", error.message);
			});
	}, [changeProfile]);
	//console.log("TEST: AUTHOR PROFILE DATA:", authProfile);

	useEffect(() => {
		async function checkRemoteFollowers(id_author) {
			await getRequest(`checkRemoteFollowers/${id_author}`);
		}

		console.log("CHECKING REMOTE FOLLOWERS");
		checkRemoteFollowers(profileUUID);

		getRequest(`authors/${profileUUID}/followers`)
			.then((data) => {
				console.log("GET followers Request Data:", data);
				setFollowers(data);
			})
			.catch((error) => {
				console.log("ERROR: ", error.message);
			});
	}, [showFollowers, changeProfile]);

	//console.log("TEST followers OUT OF REQUEST:", followers);

	useEffect(() => {
		getRequest(`authors/${profileUUID}/followings`)
			.then((data) => {
				console.log("GET followings Request Data:", data);
				setFollowings(data);
			})
			.catch((error) => {
				console.log("ERROR: ", error.message);
			});
	}, [showFollowing, changeProfile]);

	//console.log("TEST: AUTHOR followings DATA:", followings);

	useEffect(() => {
		getRequest(`authors/${profileUUID}/friends`)
			.then((data) => {
				console.log("GET friends Request Data:", data);
				setFriends(data);
			})
			.catch((error) => {
				console.log("ERROR: ", error.message);
			});
	}, [showFriends, changeProfile]);

	//console.log("TEST: AUTHOR friends DATA:", friends);

	useEffect(() => {
		getRequest(`authors/${profileUUID}/followrequests`)
			.then((data) => {
				console.log("GET followers Request Data:", data);
				setAuthFollowReqs(data);
			})
			.catch((error) => {
				console.log("ERROR: ", error.message);
			});
	}, [showReqs, changeProfile]);

	//console.log('TEST followReqs OUT OF REQUEST:', authFollowReqs);

	useEffect(() => {
		getRequest(`authors/${profileUUID}/posts`)
			.then((data) => {
				const sortedPosts = data.items.sort(
					(a, b) => new Date(b.published) - new Date(a.published)
				); // Sort the posts by their published date in descending order
				if (owner) {
					setAuthPosts(sortedPosts);
				}
				//check i profileuuid is a friend of the current user
				else if (
					friends["items"].some(
						(friend) => friend.id.split("/").slice(-1)[0] === auth.user.id
					)
				) {
					// only show public and friends posts uppercase
					const filteredPosts = sortedPosts.filter(
						(post) =>
							post.visibility.toUpperCase() === "PUBLIC" ||
							post.visibility.toUpperCase() === "FRIENDS"
					);
					setAuthPosts(sortedPosts);
				} else {
					// only show public posts
					const filteredPosts = sortedPosts.filter(
						(post) => post.visibility.toUpperCase() === "PUBLIC"
					);
					setAuthPosts(filteredPosts);
				}
			})
			.catch((error) => {
				console.log("ERROR: ", error.message);
			});
	}, [showPosts, changeProfile]);

	const [showDeleteAlert, setShowDeleteAlert] = useState(false);
	const [deletedPostId, setDeletedPostId] = useState(null);

	const handlePostDeleted = (postId) => {
		setDeletedPostId(postId);
		setShowDeleteAlert(true);
		setTimeout(() => setShowDeleteAlert(false), 3000); // Hide the alert after 3 seconds

		setAuthPosts((currentPosts) =>
			currentPosts.filter((post) => post.id !== postId)
		);
	};

	return (
		//Current User/Author, uses data from initial fetch.
		//NOTE: CURRENTLY USES DEFAULT IMAGE NO MATTER WHAT CAUSE STILL NOT SURE HOW THOSE WILL GO
		<div className="my-4 mx-56">
			<ProfileCard
				key={authProfile.id}
				url={authProfile.url}
				host={authProfile.host}
				username={authProfile.displayName}
				imageSrc={authProfile.profileImage}
				github={authProfile.github}
				buttontype={"Follow"}
				altId={profileUUID}
				owner={owner}
				viewerId={auth.user.id}
				//changeProfileFunc={flipChangeProfile}
				//change={changeProfile}
			/>

			<div className="flex justify-center">
				<div className="flex-initial flex-col h-56 grid-cols-5 gap-14 content-center">
					{buttons.map((button, index) => (
						<button
							key={index}
							onClick={() => {
								buttons.forEach((btn) => btn.stateSetter(false));
								button.stateSetter(true);
							}}
							class="text-white bg-slate-800 hover:bg-orange-500 focus:bg-orange-600 font-medium rounded-lg text-sm px-5 py-2.5 mr-8 mb-2 focus:outline-none dark:focus:bg-orange-500"
						>
							{button.name}
						</button>
					))}
				</div>
			</div>

			<div class="overflow-y-scroll max-h-screen" style={{ height: "30rem" }}>
				{showFollowers && (
					<div class="space-y-6">
						{followers["items"].map((follower) => (
							<ProfileCard
								key={follower.id}
								url={follower.url}
								host={follower.host}
								username={follower.displayName}
								imageSrc={follower.profileImage}
								authId={profileUUID}
								github={follower.github}
								owner={owner}
								//buttontype = {"Follower"} //not necessary, no button
								changeProfileFunc={flipChangeProfile}
								change={changeProfile}
								sharedBy={follower.sharedBy}
							/>
						))}
					</div>
				)}

				{showFollowing && (
					<div class="space-y-6">
						{followings["items"].map((following) => (
							<ProfileCard
								key={following.id}
								url={following.url}
								host={following.host}
								username={following.displayName}
								imageSrc={following.profileImage}
								github={following.github}
								buttontype={"Following"}
								authId={profileUUID}
								owner={owner}
								viewerId={auth.user.id}
								changeProfileFunc={flipChangeProfile}
								change={changeProfile}
							/>
						))}
					</div>
				)}

				{showFriends && (
					<div class="space-y-6">
						{friends["items"].map((friend) => (
							<ProfileCard
								key={friend.id}
								url={friend.url}
								host={friend.host}
								username={friend.displayName}
								imageSrc={friend.profileImage}
								github={friend.github}
								authId={profileUUID}
								owner={owner}
								viewerId={auth.user.id}
								changeProfileFunc={flipChangeProfile}
								change={changeProfile}
							/>
						))}
					</div>
				)}

				{showReqs && (
					<div class="space-y-6">
						{authFollowReqs["items"].map((request) => (
							<ProfileCard
								key={request["actor"].id}
								url={request["actor"].url}
								host={request["actor"].host}
								username={request["actor"].displayName}
								imageSrc={request["actor"].profileImage}
								github={request["actor"].github}
								buttontype={"Request"}
								authId={profileUUID}
								owner={owner}
								viewerId={auth.user.id}
								changeProfileFunc={flipChangeProfile}
								change={changeProfile}
							/>
						))}
					</div>
				)}
				{showDeleteAlert && (
					<Alert
						severity="success"
						style={{
							position: "absolute",
							zIndex: 2,
							width: "300px",
							height: "300px",
							marginBottom: "400px",
							marginLeft: "300px",
							display: "flex",
							flexDirection: "column",
							justifyContent: "center",
							alignItems: "center",
						}}
					>
						Post Deleted
					</Alert>
				)}

				{showPosts && (
					<div class="space-y-6">
						{authPosts.map((post) => {
							const dates = new Date(post.published);
							const formattedDate = `${dates.getFullYear()}-${String(
								dates.getMonth() + 1
							).padStart(2, "0")}-${String(dates.getDate()).padStart(2, "0")}`;
							let limitedContent = "";
							if (
								post.content !== "" &&
								(post.contentType === "text/plain" ||
									post.contentType === "text/markdown")
							) {
								limitedContent =
									post.content.length > 100
										? post.content.substring(0, 100) + "... See More"
										: post.content;
							} else {
								limitedContent = post.content;
							}
							const authorId = post.author.id.split("/").slice(-1)[0]; // extract the author's id

							const postId = post.id.split("/").slice(-1)[0]; // extract the post's id

							// const postId = post.id.split("/").slice(-1)[0]; // extract the post's id

							return (
								<PostCard
									key={post.id}
									username={post.author.displayName}
									title={post.title}
									date={formattedDate}
									description={post.description}
									contentType={post.contentType}
									content={limitedContent}
									profilePage={true}
									setAuthPosts={setAuthPosts}
									authPosts={authPosts}
									authorId={authorId}
									postId={postId}
									postVisibility={post.visibility}
									owner={owner}
									onPostDeleted={handlePostDeleted}
								/>
							);
						})}
					</div>
				)}
			</div>
		</div>
	);
}

export default Profile;
