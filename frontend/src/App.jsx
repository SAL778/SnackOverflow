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

const routes = [
	{ path: "/login", component: Login },
	{ path: "/signup", component: Signup },
	{ path: "/profile", component: Profile, isPrivate: true },
	{ path: "/profile/:source", component: Profile, isPrivate: true },
	{ path: "/", component: Feed, isPrivate: true },
	{ path: "/feed", component: Feed, isPrivate: true },
	{ path: "/explore", component: Explore, isPrivate: true },
	{ path: "/newpost", component: NewPost, isPrivate: true },
	{
		path: "/profile/:authorId/posts/:postId",
		component: SinglePost,
		isPrivate: true,
	},
	{
		path: "/edit-post/:authorId/:postId",
		component: NewPost,
		isPrivate: true,
		props: { editMode: true },
	},
];

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
					{routes.map(
						({ path, component: Component, isPrivate, props }, index) => (
							<Route
								key={index}
								path={path}
								element={
									isPrivate ? (
										<PrivateRoute>
											<Component {...props} />
										</PrivateRoute>
									) : (
										<Component {...props} />
									)
								}
							/>
						)
					)}
				</Routes>
			</div>
		</Router>
	);
}

export default App;
