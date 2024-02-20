import { Navigate } from 'react-router-dom'
import { useAuth } from './Auth.jsx'

const PrivateRoute = ({ children }) => {
    const auth = useAuth();

    // auth.user = "testuser"
    console.log("auth.user:")
    console.log(auth.user)

    return(
        auth.user ? children : <Navigate to="/login"/>
    )
}

export default PrivateRoute;