import React, { useEffect, useState } from "react";
import dummyimage from "../assets/smiley.jpg";
import dummyimage2 from "../assets/snack-logo.png";
import defaultPFP from "../assets/Default_pfp.jpg";
import ProfileCard from "../components/ProfileCard.jsx";
//card source: https://flowbite.com/docs/components/card/
import { getRequest, postRequest } from "../utils/Requests.jsx";
import { useAuth } from "../utils/Auth.jsx";

function Profile() {

	const auth = useAuth();

	const [authProfile, setAuthProfile] = useState([])
	useEffect(() => {

		getRequest(`authors/${auth.userId}`)
        .then((data) => {
            //console.log('GET author Request Data:', data);
			//console.log('GET author Request Data Attribute:', data.displayName);
			setAuthProfile(data)
        })
        .catch((error) => {
            console.log('ERROR: ', error.message);
        });

	}, []);

	console.log("TEST: AUTHOR PROFILE DATA:", authProfile);
	//END REQUEST	

	const profile = [
		{
			id: 1,
			host:"http://127.0.0.1:5173/",
			username: "Dummy One",
			imageSrc: dummyimage2,
			github: "http://github.com/", //JUST LINKS TO BASE GITHUB PAGE FOR TESTING
			}
	]

	console.log("TEST: NORMAL PROFILE DATA:", profile);

	const profile2 = [
		{
			id: 2,
			host:"http://127.0.0.1:5173/",
			username: "Dummy Twooo",
			imageSrc: dummyimage,
			github: "http://github.com/", //JUST LINKS TO BASE GITHUB PAGE FOR TESTING
			}
	]

	const profile3 = [
		{
			id: 3,
			host:"http://127.0.0.1:5173/",
			username: "Dummy Tree",
			imageSrc: dummyimage,
			github: "http://github.com/", //JUST LINKS TO BASE GITHUB PAGE FOR TESTING
			}
	]

	const profile4 = [
		{
			id: 4,
			host:"http://127.0.0.1:5173/",
			username: "Dummy Idiot",
			imageSrc: dummyimage,
			github: "http://github.com/", //JUST LINKS TO BASE GITHUB PAGE FOR TESTING
			}
	]

	const profile5 = [
		{
			id: 5,
			host:"http://127.0.0.1:5173/",
			username: "Dummy Test",
			imageSrc: dummyimage,
			github: "http://github.com/", //JUST LINKS TO BASE GITHUB PAGE FOR TESTING
			}
	]

	const [showFollowers, setShowFollowers] = useState(false);
	const [showFollowing, setShowFollowing] = useState(false);
	const [showFriends, setShowFriends] = useState(false);
	const [showPosts, setShowPosts] = useState(false);
	const [showReqs, setShowReqs] = useState(false);

	return (
		
	<div className="my-4 mx-56">
		{profile.map((profile) => (

		//Current User/Author, uses data from initial fetch.
		//NOTE: CURRENTLY USES DEFAULT IMAGE NO MATTER WHAT CAUSE STILL NOT SURE HOW THOSE WILL GO
		<ProfileCard  
			key={authProfile.id}
			host={authProfile.host}
			username={authProfile.displayName}
			imageSrc={defaultPFP}
			github={authProfile.github}
		/>
		
		))}


		<div class="flex flex-initial flex-col h-56 grid grid-cols-5 gap-14 content-center">
				<button onClick={()=> {setShowFollowers(true); setShowFollowing(false); setShowFriends(false); setShowPosts(false); setShowReqs(false); }} 
				class="text-white bg-slate-800 hover:bg-orange-500 focus:bg-orange-600 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 focus:outline-none dark:focus:bg-orange-500">
					Followers
				</button>
				<button onClick={()=> {setShowFollowers(false); setShowFollowing(true); setShowFriends(false); setShowPosts(false); setShowReqs(false); }} 
				class="text-white bg-slate-800 hover:bg-orange-500 focus:bg-orange-600 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 focus:outline-none dark:focus:bg-orange-500">
					Following
				</button>
				<button onClick={()=> {setShowFollowers(false); setShowFollowing(false); setShowFriends(true); setShowPosts(false); setShowReqs(false); }} 
				class="text-white bg-slate-800 hover:bg-orange-500 focus:bg-orange-600 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 focus:outline-none dark:focus:bg-orange-500">
					Friends
				</button>
				<button onClick={()=> {setShowFollowers(false); setShowFollowing(false); setShowFriends(false); setShowPosts(true); setShowReqs(false); }} 
				class="text-white bg-slate-800 hover:bg-orange-500 focus:bg-orange-600 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 focus:outline-none dark:focus:bg-orange-500">
					Posts
				</button>
				<button onClick={()=> {setShowFollowers(false); setShowFollowing(false); setShowFriends(false); setShowPosts(false); setShowReqs(true); }} 
				class="text-white bg-slate-800 hover:bg-orange-500 focus:bg-orange-600 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 focus:outline-none dark:focus:bg-orange-500">
					Follow Requests
				</button>
			</div>
		
		

			<div class="overflow-y-scroll h-96 max-h-screen">
				{ showFollowers &&
				<div class="space-y-6">
					{profile2.map((profile) => (

						<ProfileCard  
							key={profile.id}
							host={profile.host}
							username={profile.username}
							imageSrc={profile.imageSrc}
							github={profile.github}
						/>

					))}

					{profile3.map((profile) => (

						<ProfileCard  
							key={profile.id}
							host={profile.host}
							username={profile.username}
							imageSrc={profile.imageSrc}
							github={profile.github}
						/>

					))}

				
					{profile4.map((profile) => (

						<ProfileCard  
							key={profile.id}
							host={profile.host}
							username={profile.username}
							imageSrc={profile.imageSrc}
							github={profile.github}
						/>

					))}

				</div>
					}

				{ showFollowing &&

				<div class="space-y-6">

				{profile4.map((profile) => (

				<ProfileCard  
					key={profile.id}
					host={profile.host}
					username={profile.username}
					imageSrc={profile.imageSrc}
					github={profile.github}
				/>

				))}
				
				
				</div>

								}

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