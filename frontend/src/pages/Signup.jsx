import React from "react";
import logo from "../assets/snack-logo.png";
import Box from "@mui/material/Box";
import TextField from "@mui/material/TextField";
import { Button, Typography } from "@mui/material";
import { Link } from "react-router-dom";
import { createTheme, ThemeProvider } from "@mui/material/styles";
import { orange } from "@mui/material/colors";
import { useAuth } from "../utils/Auth.jsx";
import Alert from "@mui/material/Alert";
import CheckIcon from "@mui/icons-material/Check";
import { useNavigate } from "react-router-dom";

const theme = createTheme({
	palette: {
		primary: orange,
	},
});

// This signup page has a few components/functionality taken from this base template written by Material UI SAS and their contributors:
// https://github.com/mui/material-ui/tree/v5.15.11/docs/data/material/getting-started/templates/sign-up
// Accessed 2024-02-26

function Signup() {
	const auth = useAuth();
	const navigate = useNavigate();
	const [error, setError] = React.useState(null);
	const [data, setData] = React.useState(null);

	const handleSubmit = async (event) => {
		event.preventDefault();
		const data = new FormData(event.currentTarget);
		// attempt to log in user after submission of information to server
		try {
			// check if it is has github in the github field
			console.log(data.get("github").split("/")[3]);
			if (data.get("github").slice(8,18) !== "github.com") {
				throw new Error("Github field does not contain the github website.");
			}
			const response = await auth.register(
				data.get("email"),
				data.get("password"),
				data.get("display_name"),
				data.get("github"),
				data.get("profile_image")
			);
			setError(null);
			setData(response);
			console.log(response);
			// redirect to login page
			setTimeout(() => {
				navigate("/login");
			}, 2000);
		} catch (error) {
			if (error.message.includes("Github")) {
				setError("Please fill in a valid Github user URL.");
			} else{
				setError("An error occured when registering. Please try again.");
			}
			setData(null);
		}
	};

	return (
		<ThemeProvider theme={theme}>
			<div className="flex flex-col h-screen w-screen items-center justify-center bg-gray-200 p-5">
				{/* alerts show up if there is an error or successful registration */}
				{error && (
					<Alert severity="error">
						{error}
					</Alert>
				)}
				{data && (
					<Alert icon={<CheckIcon fontSize="inherit" />} severity="success">
						Registration was successful! Redirecting to sign in page...
					</Alert>
				)}
				<Box
					className="flex flex-initial flex-col items-center justify-center bg-white rounded-md shadow-md h-fit w-3/12 p-2"
					component="form"
					sx={{
						"& .MuiTextField-root": { m: 1, width: "25ch" },
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
						helperText="Format: https://github.com/user"
					/>
					<TextField
						fullWidth
						id="profile_image"
						label="Profile Image"
						size="small"
						name="profile_image"
						helperText="Format: https://"
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
					<Link className="text-orange-500 hover:underline" to="/login/">
						Have an account? Sign in.
					</Link>
				</Box>
			</div>
		</ThemeProvider>
	);
}

export default Signup;
