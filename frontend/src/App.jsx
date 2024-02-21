import { React, useState } from "react";
import "./App.css";
import "./output.css";
import Navigation from "./components/Navbar.jsx";
import NotificationBar from "./components/Notifbar.jsx";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Profile from "./components/Profile.jsx";
import Feed from "./components/Feed.jsx";
import Explore from "./components/Explore.jsx";
import NewPost from "./components/NewPost.jsx";
import Login from "./components/Login.jsx";
import Welcome from "./components/Welcome.jsx";
import PrivateRoute from "./utils/PrivateRoute.jsx";
import { AuthProvider, useAuth } from "./utils/Auth.jsx";

function App() {

	const auth = useAuth();

	return (
		<Router>
			<div className="flex h-screen w-screen flex-col md:flex-row md:overflow-hidden bg-gray-200">
				{
					auth.user ? 
						<div className="flex-none md:w-60">
							<Navigation />
						</div> 
					: null
				}
				
				<Routes>
				    <Route path="/login" element={<Login />} />

					<Route path="/" element={ <PrivateRoute> < Welcome /> </PrivateRoute> }/>
					<Route path="/profile" element={<PrivateRoute> <Profile /> </PrivateRoute> } />
					<Route path="/feed" element={ <PrivateRoute> <Feed /> </PrivateRoute>} />
					<Route path="/explore" element={ <PrivateRoute> <Explore /> </PrivateRoute>} />
					<Route path="/newpost" element={ <PrivateRoute> <NewPost /> </PrivateRoute>} />


				</Routes>

				{
					auth.user ? <NotificationBar /> : null
				}

				
			</div>
		</Router>
	);
}

export default App;
