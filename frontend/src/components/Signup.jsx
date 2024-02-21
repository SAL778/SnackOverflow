import React from "react";
import logo from "../assets/snack-logo.png";
import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';

function Signup() {
	return (
		<div className="flex h-screen w-screen items-center justify-center bg-gray-200 p-5">
			<Box
				className="flex flex-initial flex-col align-content-center bg-white rounded-md shadow-md h-4/6 w-3/12 p-4"
				component="form"
				sx={{
					'& .MuiTextField-root': { m: 1, width: '25ch' },
				}}
				noValidate
				autoComplete="off"
			>
				<img
					className="p-5"
					src={logo}
					alt="Snack Overflow icon"
					width={400}
					height={40}
				/>
				<TextField
				id="username"
				label="Username"
				/>
				<TextField
				id="password"
				label="Password"
				type="password"
				autoComplete="current-password"
				/>
			</Box>
		</div>
	);
}

export default Signup;
