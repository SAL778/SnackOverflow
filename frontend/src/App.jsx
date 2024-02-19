import React from "react";
import "./App.css";
import "./output.css";
import Navigation from "./components/Navbar.jsx";
import NotificationBar from "./components/Notifbar.jsx";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Profile from "./components/Profile.jsx";
import Feed from "./components/Feed.jsx";
import Explore from "./components/Explore.jsx";
import NewPost from "./components/NewPost.jsx";

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
