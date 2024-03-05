import React, {
	useEffect,
	useInsertionEffect,
	useState,
	forceUpdate,
} from "react";
import dummyimage from "../assets/smiley.jpg";
import dummyimage2 from "../assets/snack-logo.png";
import defaultPFP from "../assets/Default_pfp.jpg";
import ProfileCard from "../components/ProfileCard.jsx";
import PostCard from "../components/PostCard.jsx";
import { getRequest, postRequest } from "../utils/Requests.jsx";
import { useAuth } from "../utils/Auth.jsx";
import { useParams } from "react-router-dom";
import { Link } from "react-router-dom";

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

	const [changeProfile, setChangeProfile] = useState(false);
	const flipChangeProfile = (change) => {
		setChangeProfile(!change);
	};

	let profileUUID = auth.user.id;
	let owner = true;

	if (source === undefined) {
		console.log("No source, portay profile as logged-in user");
		profileUUID = auth.user.id; //redundant but explicit
		owner = true; //redundant but explicit
	} else if (source === profileUUID) {
		console.log("Accessing Own Profile.");
		profileUUID = auth.user.id; //redundant but explicit
		owner = true; //redundant but explicit
	} else {
		//ASSUMING THAT THE SOURCE IS VALID
		profileUUID = source;
		owner = false;
	}

	//BEGIN AUTHOR FETCH

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
	console.log("TEST: AUTHOR PROFILE DATA:", authProfile);

	//END AUTHOR FETCH

	//BEGIN AUTHOR FOLLOWERS FETCH
	useEffect(() => {
		getRequest(`authors/${profileUUID}/followers`)
			.then((data) => {
				console.log("GET followers Request Data:", data);
				setFollowers(data);
			})
			.catch((error) => {
				console.log("ERROR: ", error.message);
			});
	}, [showFollowers, changeProfile]);

	console.log("TEST followers OUT OF REQUEST:", followers);

	//END AUTHOR FOLLOWERS FETCH

	//BEGIN AUTHOR FOLLOWINGS FETCH

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

	//END AUTHOR FOLLOWINGS FETCH

	console.log("TEST: AUTHOR followings DATA:", followings);

	//BEGIN AUTHOR FRIENDS FETCH

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

	//END AUTHOR FOLLOWINGS FETCH

	console.log("TEST: AUTHOR friends DATA:", friends);

	//END AUTHOR FOLLOWERS FETCH

	//BEGIN AUTHOR FOLLOWREQS FETCH
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
				console.log("GET posts Request Data:", data);
				const sortedPosts = data.items.sort(
					(a, b) => new Date(b.published) - new Date(a.published)
				); // Sort the posts by their published date in descending order
				setAuthPosts(sortedPosts);
			})
			.catch((error) => {
				console.log("ERROR: ", error.message);
			});
	}, [showPosts, changeProfile]);

	return (
		//Current User/Author, uses data from initial fetch.
		//NOTE: CURRENTLY USES DEFAULT IMAGE NO MATTER WHAT CAUSE STILL NOT SURE HOW THOSE WILL GO
		<div className="my-4 mx-56">
			<ProfileCard
				key={authProfile.id}
				url={authProfile.url}
				host={authProfile.host}
				username={authProfile.displayName}
				imageSrc={defaultPFP}
				github={authProfile.github}
				buttontype={"Follow"}
				altId={profileUUID}
				owner={owner}
				viewerId={auth.user.id}
				//changeProfileFunc={flipChangeProfile}
				//change={changeProfile}
			/>

			<div className="flex-initial flex-col h-56 grid-cols-5 gap-14 content-center">
				<button
					onClick={() => {
						setShowFollowers(true);
						setShowFollowing(false);
						setShowFriends(false);
						setShowPosts(false);
						setShowReqs(false);
					}}
					class="text-white bg-slate-800 hover:bg-orange-500 focus:bg-orange-600 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 focus:outline-none dark:focus:bg-orange-500"
				>
					Followers
				</button>
				<button
					onClick={() => {
						setShowFollowers(false);
						setShowFollowing(true);
						setShowFriends(false);
						setShowPosts(false);
						setShowReqs(false);
					}}
					class="text-white bg-slate-800 hover:bg-orange-500 focus:bg-orange-600 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 focus:outline-none dark:focus:bg-orange-500"
				>
					Following
				</button>
				<button
					onClick={() => {
						setShowFollowers(false);
						setShowFollowing(false);
						setShowFriends(true);
						setShowPosts(false);
						setShowReqs(false);
					}}
					class="text-white bg-slate-800 hover:bg-orange-500 focus:bg-orange-600 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 focus:outline-none dark:focus:bg-orange-500"
				>
					Friends
				</button>
				<button
					onClick={() => {
						setShowFollowers(false);
						setShowFollowing(false);
						setShowFriends(false);
						setShowPosts(true);
						setShowReqs(false);
					}}
					class="text-white bg-slate-800 hover:bg-orange-500 focus:bg-orange-600 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 focus:outline-none dark:focus:bg-orange-500"
				>
					Posts
				</button>
				<button
					onClick={() => {
						setShowFollowers(false);
						setShowFollowing(false);
						setShowFriends(false);
						setShowPosts(false);
						setShowReqs(true);
					}}
					class="text-white bg-slate-800 hover:bg-orange-500 focus:bg-orange-600 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 focus:outline-none dark:focus:bg-orange-500"
				>
					Follow Requests
				</button>
			</div>

			<div class="overflow-y-scroll h-96 max-h-screen">
				{showFollowers && (
					<div class="space-y-6">
						{followers["items"].map((follower) => (
							<ProfileCard
								key={follower.id}
								url={follower.url}
								host={follower.host}
								username={follower.displayName}
								imageSrc={dummyimage}
								authId={profileUUID}
								github={follower.github}
								owner={owner}
								//buttontype = {"Follower"} //not necessary, no button
								changeProfileFunc={flipChangeProfile}
								change={changeProfile}
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
								imageSrc={dummyimage}
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
								imageSrc={dummyimage}
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
								imageSrc={dummyimage}
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

				{showPosts && (
					<div class="space-y-6">
						{authPosts.map((post) => {
							const dates = new Date(post.published);
							const formattedDate = `${dates.getFullYear()}-${String(
								dates.getMonth() + 1
							).padStart(2, "0")}-${String(dates.getDate()).padStart(2, "0")}`;

							const limitedContent =
								post.content.length > 100
									? post.content.substring(0, 100) + "... See More"
									: post.content;

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
									postId={post.id}
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

//	<div>
// {profile.map((profile) => (

// 		<ProfileCard
// 			key={profile.id}
// 			host={profile.host}
// 			username={profile.username}
// 			imageSrc={profile.imageSrc}
// 			github={profile.github}
// 		/>

// ))}
// </div>
