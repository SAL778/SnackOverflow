import React from "react";
import logo from "../assets/snack-logo.png";
import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import { Button, Typography } from "@mui/material";
import { Link, Navigate } from "react-router-dom";
import { createTheme, ThemeProvider } from '@mui/material/styles';
import { orange } from "@mui/material/colors";
import { useAuth } from "../utils/Auth.jsx";

const theme = createTheme({
	palette: {
	  primary: orange,
	},
  });
  

function Signup() {

	const auth = useAuth();

	const handleSubmit = (event) => {
		event.preventDefault();
		const data = new FormData(event.currentTarget);
		console.log({
		  email: data.get('email'),
		  password: data.get('password'),
		  displayname: data.get('display_name'),
		  github: data.get('github'),
		  profileimage: data.get('profile_image')
		});

		auth.register(data.get('email'), data.get('password'), data.get('display_name'), data.get('github'), data.get('profile_image'));
		<Navigate to="/" replace={true}/>;
		// if submission valid, redirect to /feed
		// if submission valid but signup restriction, indicate success but do not redirect
		// if submission invalid, indicate error
	};
	

	return (
		<ThemeProvider theme={theme}>
			<div className="flex h-screen w-screen items-center justify-center bg-gray-200 p-5">
				<Box
					className="flex flex-initial flex-col items-center justify-center bg-white rounded-md shadow-md h-fit w-4/12 p-4"
					component="form"
					sx={{
						'& .MuiTextField-root': { m: 1, width: '25ch' },
					}}
					noValidate
					onSubmit={handleSubmit}
					autoComplete="off"
				>
					<img
						className="p-2"
						src={logo}
						alt="Snack Overflow icon"
						width={400}
						height={40}
					/>
					<Typography component="h1" variant="h5">
						Sign up
					</Typography>
					<TextField
						required
						fullWidth
						id="email"
						label="Email"
						size="small"
						name="email"
						autoComplete="email"
					/>
					<TextField
						required
						fullWidth
						name="password"
						label="Password"
						type="password"
						id="password"
						size="small"
						autoComplete="new-password"
					/>
					<TextField
						required
						fullWidth
						id="display_name"
						label="Display Name"
						size="small"
						name="display_name"
					/>
					<TextField
						required
						fullWidth
						id="github"
						name="github"
						label="GitHub Profile"
						size="small"
					/>
					<TextField
						fullWidth
						id="profile_image"
						label="Profile Image"
						size="small"
						name="profile_image"
					/>
					<Button 
						variant="contained" 
						color="primary"
						sx={{ 
							mt: 3, 
							mb: 2,
						}}
						type="submit"
					>
						Sign Up
					</Button>
					<Link className="text-orange-700 hover:underline" to="/login/">
						Have an account? Sign in.
					</Link>
				</Box>
			</div>
		</ThemeProvider>
	);
}

export default Signup;
