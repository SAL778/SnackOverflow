// This file has been adapted from the following source:
// - https://dev.to/dayvster/use-react-context-for-auth-288g
// - https://medium.com/@remind.stephen.to.do.sth/hands-on-guide-to-secure-react-routes-with-authentication-context-971f37ede990
// Accessed 2024-02-22

import { createContext, useState, useContext, useEffect } from "react";
import { getRequest, postRequest } from "./Requests.jsx";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
	const [user, setUser] = useState(
		localStorage.getItem("user")
			? JSON.parse(localStorage.getItem("user"))
			: null
	);
	const [isLoggedIn, setIsLoggedIn] = useState(
		localStorage.getItem("isLoggedIn") === "true"
	);

	const login = async (email, password) => {
		try {
			const response = await postRequest("login/", { email, password }, false);

			setUser(response);
			setIsLoggedIn(true);

			console.log("User: ", user);

			const userId = extractUUID(response.id);
			response.id = userId;

			localStorage.setItem("user", JSON.stringify(response));
			localStorage.setItem("isLoggedIn", "true");
			localStorage.setItem("polling", "false");

			return new Promise((resolve) => {
				resolve(true);
			});
		} catch (error) {
			console.error("Error logging in:", error);
			return new Promise(() => {
				throw error;
			});
		}
	};

	const logout = async () => {
		try {
			const response = await postRequest("logout/", {});

			setUser(null);
			setIsLoggedIn(false);

			localStorage.removeItem("user");
			// localStorage.removeItem("userId");
			localStorage.setItem("isLoggedIn", "false");
			localStorage.setItem("polling", "false");
		} catch (error) {
			console.error("Error logging out:", error);
		}
	};

	const register = async (
		email,
		password,
		displayname,
		github,
		profileimage
	) => {
		try {
			const response = await postRequest(
				"register/",
				{
					email: email,
					password: password,
					display_name: displayname,
					github: github,
					profile_image: profileimage,
				},
				false
			);

			return new Promise((resolve) => {
				resolve(true);
			});
		} catch (error) {
			console.error("Error registering:", error);
			return new Promise(() => {
				throw error;
			});
		}
	};

	return (
		<AuthContext.Provider value={{ user, isLoggedIn, login, logout, register }}>
			{children}
		</AuthContext.Provider>
	);
};

export const useAuth = () => {
	return useContext(AuthContext);
};

export function extractUUID(url) {
	let parts = url.split("/");
	return parts[parts.length - 1];
}
