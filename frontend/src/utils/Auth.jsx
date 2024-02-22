import { createContext, useState, useContext, useEffect } from 'react';
import axios from "axios";

const AuthContext = createContext(null);

// ensure the CSRF token is sent with requests
axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.xsrfHeaderName = 'X-CSRFToken';
axios.defaults.withCredentials = true;

const client = axios.create({
  baseURL: "http://127.0.0.1:8000"
  // can add headers here
});

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(localStorage.getItem('user') || null);
    const [isLoggedIn, setIsLoggedIn] = useState(localStorage.getItem('isLoggedIn') === 'true');

    // to determine if the user is logged in
    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await client.get("/api/user/", { withCredentials: true });
                setUser(response.data.user.displayName);
                setIsLoggedIn(true);

                // localStorage.setItem('user', response.data.displayName);
                // localStorage.setItem('isLoggedIn', 'true');

                console.log("inside useEffect");
                console.log(response.data);
                console.log(response.data.user.displayName);
                console.log("-----------------");


            } catch (error) {
                setUser(null);
                setIsLoggedIn(false);
                console.error("Error fetching user data:", error);
            }
        };
        fetchData();
    }, [user]);


    const login = async (email, password) => {
        try {
            const response = await client.post("/api/login/", { email, password });
            setUser(response.data.email);
            setIsLoggedIn(true);

            localStorage.setItem('user', response.data.email);
            localStorage.setItem('isLoggedIn', 'true');

            console.log("login");
            console.log(isLoggedIn);
            console.log("User: " + user);
            console.log(response.data);
            console.log("-----------------");
            return new Promise((resolve) => {
                resolve(true);
            });

        } catch (error) {
            console.error("Error logging in:", error);
            console.log("User: " + user);
            return new Promise(() => {
                throw error;
            });
        }
    }


    const logout = async () => {
        try {
            const response = await client.post("/api/logout/", { withCredentials: true });
            setUser(null);
            setIsLoggedIn(false);

            localStorage.removeItem('user');
            localStorage.setItem('isLoggedIn', 'false');

            console.log("logout");
            console.log(isLoggedIn);
            console.log(user);
            console.log(response.data);
            console.log("-----------------");

        } catch (error) {
            console.error("Error logging out:", error);
        }
    }

    const register = async (email, password, displayname, github, profileimage) => {
        try {
            const response = await client.post("/api/register/", {
                email: email,
                password: password,
                display_name: displayname,
                github: github,
                profile_image: profileimage
            });

            console.log("register");
            console.log(isLoggedIn);
            console.log(response.data);
            console.log("-----------------");
            // return true;
            return new Promise((resolve) => {
                resolve(true);
            });

        } catch (error) {
            console.error("Error registering:", error);
            return new Promise(() => {
                throw error;
            });
        }
    }

    return (
        <AuthContext.Provider value={{ user, isLoggedIn, login, logout, register }}>
            { children }
        </AuthContext.Provider>
    )
}

export const useAuth = () => {
    return useContext(AuthContext)
}