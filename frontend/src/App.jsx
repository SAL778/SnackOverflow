// import "./App.css";
// import Navigation from "./components/Navbar.jsx";
// import NotificationBar from "./components/Notifbar.jsx";

// function App() {
// 	return (
// 		<div className="flex h-screen w-screen flex-col md:flex-row md:overflow-hidden bg-gray-200">
// 			<div className="flex-none md:w-60">
// 				<Navigation />
// 			</div>
// 			<div class="flex flex-1 bg-gray-300 mx-4 my-3 h-16 p-4">Header</div>
// 			<NotificationBar />
// 		</div>
// 	);
// }

// export default App;

import React from "react";
import "./App.css";
import Navigation from "./components/Navbar.jsx";
import NotificationBar from "./components/Notifbar.jsx";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Profile from "./Profile.jsx";
import Feed from "./Feed.jsx";
import Explore from "./Explore.jsx";
import NewPost from "./NewPost.jsx";

function App() {
	return (
		<Router>
			<div className="flex h-screen w-screen flex-col md:flex-row md:overflow-hidden bg-gray-200">
				<div className="flex-none md:w-60">
					<Navigation />
				</div>
				<Routes>
					<Route path="/profile" element={<Profile />} />
					<Route path="/feed" element={<Feed />} />
					<Route path="/explore" element={<Explore />} />
					<Route path="/newpost" element={<NewPost />} />
				</Routes>
				<NotificationBar />
			</div>
		</Router>
	);
}

export default App;
