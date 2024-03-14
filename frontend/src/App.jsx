import { React, useState } from "react";
import "./App.css";
import "./output.css";
import Navigation from "./components/Navbar.jsx";
import SinglePost from "./components/SinglePost.jsx";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Profile from "./pages/Profile.jsx";
import Feed from "./pages/Feed.jsx";
import Explore from "./pages/Explore.jsx";
import NewPost from "./pages/NewPost.jsx";
import Login from "./pages/Login.jsx";
import PrivateRoute from "./utils/PrivateRoute.jsx";
import { AuthProvider, useAuth } from "./utils/Auth.jsx";
import Signup from "./pages/Signup.jsx";

function App() {
	const auth = useAuth();

	return (
		<Router>
			<div className="flex h-screen w-screen flex-col md:flex-row md:overflow-hidden bg-gray-200">
				{auth.user ? (
					<div className="flex-none md:w-60">
						<Navigation />
					</div>
				) : null}

				<Routes>
					<Route path="/login" element={<Login />} />
					<Route path="/signup" element={<Signup />} />

					<Route
						path="/profile"
						element={
							<PrivateRoute>
								<Profile />
							</PrivateRoute>
						}
					/>
					<Route
						path="/profile/:source"
						element={
							<PrivateRoute>
								<Profile />
							</PrivateRoute>
						}
					/>
					<Route
						path="/"
						element={
							<PrivateRoute>
								<Feed />
							</PrivateRoute>
						}
					/>
					<Route
						path="/feed"
						element={
							<PrivateRoute>
								<Feed />
							</PrivateRoute>
						}
					/>
					<Route
						path="/explore"
						element={
							<PrivateRoute>
								<Explore />
							</PrivateRoute>
						}
					/>
					<Route
						path="/newpost"
						element={
							<PrivateRoute>
								<NewPost />
							</PrivateRoute>
						}
					/>
					<Route
						path="/profile/:authorId/posts/:postId"
						element={
							<PrivateRoute>
								<SinglePost />
							</PrivateRoute>
						}
					/>
				</Routes>
			</div>
		</Router>
	);
}

export default App;
