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
    const [user, setUser] = useState();
    const [isLoggedIn, setIsLoggedIn] = useState();
    const [isLoading, setIsLoading] = useState(true); // Add isLoading state


    // to determine if the user is logged in
    useEffect(() => {
        client.get(
            "/api/user/", 
            {withCredentials: true}
        ).then(function(res) {
            console.log("inside useEffect");
            console.log(res.data);
            console.log(res.data.user.displayName);
            console.log("-----------------");

            setUser(res.data.user.displayName);
            setIsLoggedIn(true);
            setIsLoading(false); // Set isLoading to false when data is fetched

        })
        .catch(function(error) {
            console.log("inside useEffect error");
            console.log(error);
            console.log("-----------------");

            setUser(null);
            setIsLoggedIn(false);
            setIsLoading(false); // Set isLoading to false even if there's an error
        });
    }, []);


    const login = (email, password) => {
        client.post(
            "/api/login/",
            {
                email: email,
                password: password
            }
        ).then(function(res) {
            setUser(res.data.email);
            setIsLoggedIn(true);

            console.log("login");
            console.log(isLoggedIn);
            console.log(user);
            console.log(res.data);
            console.log("-----------------");
        }
        ).catch(function(error) {
            console.log(error);
        });
    }


    const logout = () => {
        client.post(
            "/api/logout/",
            {withCredentials: true}
        ).then(function(res) {
            setUser(null);
            setIsLoggedIn(false);

            console.log("logout");
            console.log(isLoggedIn);
            console.log(user);
            console.log(res.data);
            console.log("-----------------");

        });
    }

    return (
        <AuthContext.Provider value={{ user, isLoggedIn, login, logout }}>
            {isLoading ? <div>Loading...</div> : children} {/* Render children only when isLoading is false */}
        </AuthContext.Provider>
    )
}

export const useAuth = () => {
    return useContext(AuthContext)
}