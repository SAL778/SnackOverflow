import React, { useEffect, useInsertionEffect, useState } from "react";
import dummyimage from "../assets/smiley.jpg";
import dummyimage2 from "../assets/snack-logo.png";
import defaultPFP from "../assets/Default_pfp.jpg";
import ProfileCard from "../components/ProfileCard.jsx";
import PostCard from "../components/PostCard.jsx";
//card source: https://flowbite.com/docs/components/card/
import { getRequest, postRequest } from "../utils/Requests.jsx";
import { useAuth } from "../utils/Auth.jsx";

function Profile() {
	const owner = true; //TO BE USED LATER FOR IMPLENETING DIFFERENCES BETWEEN OWN PROFILE VS OTHER USER PROFILES
	const auth = useAuth();

	console.log("TEST AUTH LOOOOOOOOOOK", auth);

	const [authProfile, setAuthProfile] = useState([]);
	const [followers, setFollowers] = useState([]);
	const [followings, setFollowings] = useState([]);
	const [authPosts, setAuthPosts] = useState([]);
	const [authFollowReqs, setAuthFollowReqs] = useState([]);

	const [showFollowers, setShowFollowers] = useState(false);
	const [showFollowing, setShowFollowing] = useState(false);
	const [showFriends, setShowFriends] = useState(false);
	const [showPosts, setShowPosts] = useState(false);
	const [showReqs, setShowReqs] = useState(false);

	//BEGIN AUTHOR FETCH
	useEffect(() => {
		getRequest(`authors/${auth.userId}`)
			.then((data) => {
				//console.log('GET author Request Data:', data);
				//console.log('GET author Request Data Attribute:', data.displayName);
				setAuthProfile(data);
			})
			.catch((error) => {
				console.log("ERROR: ", error.message);
			});
	}, []);

	console.log("TEST: AUTHOR PROFILE DATA:", authProfile);
	//END AUTHOR FETCH

	//BEGIN AUTHOR FOLLOWERS FETCH
	useEffect(() => {
		getRequest(`authors/${auth.userId}/followers`)
			.then((data) => {
				console.log("GET followers Request Data:", data);
				setFollowers(data);
			})
			.catch((error) => {
				console.log("ERROR: ", error.message);
			});
	}, []);

	console.log("TEST followers OUT OF REQUEST:", followers);

	//END AUTHOR FOLLOWERS FETCH

	//BEGIN AUTHOR FOLLOWREQS FETCH
	useEffect(() => {
		getRequest(`authors/${auth.userId}/followrequests`)
			.then((data) => {
				console.log("GET followers Request Data:", data);
				setAuthFollowReqs(data);
			})
			.catch((error) => {
				console.log("ERROR: ", error.message);
			});
	}, []);

	console.log("TEST followReqs OUT OF REQUEST:", authFollowReqs);

	// END AUTHOR FOLLOWREQS FETCH

	//BEGIN AUTHOR POSTS FETCH
	// useEffect(() => {
	// 	getRequest(`authors/${auth.userId}/posts`)
	// 	.then((data) => {
	// 		console.log('GET posts Request Data:', data);
	// 		setAuthPosts(data);
	// 	})
	// 	.catch((error) => {
	// 		console.log('ERROR: ', error.message);
	// 	});
	// }, [showPosts]);
	useEffect(() => {
		getRequest(`authors/${auth.userId}/posts`) // post id is not being used?
			.then((data) => {
				console.log("GET posts Request Data:", data);
				setAuthPosts(data.items);
				console.log("TEST posts OUT OF REQUEST:", authPosts);
			})
			.catch((error) => {
				console.log("ERROR: ", error.message);
			});
	}, [showPosts]);

	console.log("TEST posts OUT OF REQUEST:", authPosts);
	console.log(auth.userId);
	console.log("TEST posts OUT OF REQUEST:", authPosts);
	const profile4 = [
		{
			id: 4,
			host: "http://127.0.0.1:5173/",
			username: "Dummy Idiot",
			imageSrc: dummyimage,
			github: "http://github.com/", //JUST LINKS TO BASE GITHUB PAGE FOR TESTING
		},
	];

	const profile5 = [
		{
			id: 5,
			host: "http://127.0.0.1:5173/",
			username: "Dummy Test",
			imageSrc: dummyimage,
			github: "http://github.com/", //JUST LINKS TO BASE GITHUB PAGE FOR TESTING
		},
	];

	return (
		//Current User/Author, uses data from initial fetch.
		//NOTE: CURRENTLY USES DEFAULT IMAGE NO MATTER WHAT CAUSE STILL NOT SURE HOW THOSE WILL GO
		<div className="my-4 mx-56">
			<ProfileCard
				key={authProfile.id}
				host={authProfile.host}
				username={authProfile.displayName}
				imageSrc={defaultPFP}
				github={authProfile.github}
			/>

			<div class="flex flex-initial flex-col h-56 grid grid-cols-5 gap-14 content-center">
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
								host={follower.host}
								username={follower.displayName}
								imageSrc={dummyimage}
								github={follower.github}
								//buttontype = {"Follower"}
							/>
						))}
					</div>
				)}

				{showFollowing && (
					<div class="space-y-6">
						{profile4.map((profile) => (
							<ProfileCard
								key={profile.id}
								host={profile.host}
								username={profile.username}
								imageSrc={profile.imageSrc}
								github={profile.github}
								buttontype={"Following"}
								authId={auth.userId}
							/>
						))}
					</div>
				)}

				{showReqs && (
					<div class="space-y-6">
						{authFollowReqs["items"].map((request) => (
							<ProfileCard
								key={request["actor"].id}
								host={request["actor"].host}
								username={request["actor"].displayName}
								imageSrc={dummyimage}
								github={request["actor"].github}
								buttontype={"Request"}
								authId={auth.userId}
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
