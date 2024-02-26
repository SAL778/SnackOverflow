import React from "react";
import { useAuth } from "../utils/Auth.jsx";

function Welcome() {
	const auth = useAuth();

	return (
		<div>
			<h1>Welcome {auth.user}</h1>
		</div>
	);
}

export default Welcome;
