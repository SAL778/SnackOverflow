import { Navigate } from 'react-router-dom'
import { useAuth } from './Auth.jsx'
import { useEffect } from 'react';

const PrivateRoute = ({ children }) => {
    const auth = useAuth();

    useEffect(() => {
        console.log("PrivateRoute useEffect")
    }, [auth.user]);

    console.log("auth.user:")
    console.log(auth.user)

    return(
        auth.user ? children : <Navigate to="/login"/>
    )
}

export default PrivateRoute;