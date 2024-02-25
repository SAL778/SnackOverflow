import { Navigate } from 'react-router-dom'
import { useAuth } from './Auth.jsx'
import { useEffect } from 'react';

const PrivateRoute = ({ children }) => {
    const auth = useAuth();

    console.log("auth.user: ", auth.user);

    return(
        auth.user ? children : <Navigate to="/login"/>
    )
}

export default PrivateRoute;