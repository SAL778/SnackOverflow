import * as React from "react";
import Button from "@mui/material/Button";
import CssBaseline from "@mui/material/CssBaseline";
import TextField from "@mui/material/TextField";
import Link from "@mui/material/Link";
import Grid from "@mui/material/Grid";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Container from "@mui/material/Container";
import { createTheme, ThemeProvider } from "@mui/material/styles";
// import { pollGithub } from "../utils/Github.jsx";

import { useNavigate, Navigate } from "react-router-dom";
import { useAuth } from "../utils/Auth.jsx";
import { orange } from "@mui/material/colors";
import logo from "../assets/snack-logo.png";
import Alert from "@mui/material/Alert";

const theme = createTheme({
	palette: {
		primary: orange,
	},
});

// This login page has been adapted from this base template written by Material UI SAS and their contributors:
// https://github.com/mui/material-ui/tree/v5.15.11/docs/data/material/getting-started/templates/sign-up
// Accessed 2024-02-22

export default function Login() {
	const auth = useAuth();
	const navigate = useNavigate();
	const [error, setError] = React.useState(null);

	const handleLogin = async (event) => {
		event.preventDefault();
		const data = new FormData(event.currentTarget);

		// try to log in the user to the server
		try {
			await auth.login(data.get("email"), data.get("password"));
			setError(null);
			navigate("/feed");
		} catch (error) {
			if (error.message.includes("User has not been activated yet")) {
				setError(
					"Your account has not been activated. Please contact the administrator."
				);
			} else {
				setError("Invalid credentials. Please try again.");
			}
		}
	};

	return auth.user ? (
		<Navigate to="/feed" />
	) : (
		<ThemeProvider theme={theme}>
			<Container component="main" maxWidth="xs">
				{/* Error will display if unable to log in. */}
				{error && <Alert severity="error">{error}</Alert>}
				<CssBaseline />
				<Box
					className="bg-white rounded-md shadow-md p-5"
					sx={{
						marginTop: 8,
						display: "flex",
						flexDirection: "column",
						alignItems: "center",
					}}
				>
					<img
						className="p-2"
						src={logo}
						alt="Snack Overflow icon"
						width={400}
						height={40}
					/>
					<Typography component="h1" variant="h5">
						Sign in
					</Typography>
					<Box
						component="form"
						onSubmit={handleLogin}
						noValidate
						sx={{ mt: 1 }}
					>
						<TextField
							margin="normal"
							required
							fullWidth
							id="email"
							label="Email Address"
							name="email"
							autoComplete="email"
							autoFocus
						/>
						<TextField
							margin="normal"
							required
							fullWidth
							name="password"
							label="Password"
							type="password"
							id="password"
							autoComplete="current-password"
						/>

						<Button
							type="submit"
							fullWidth
							variant="contained"
							sx={{ mt: 3, mb: 2 }}
						>
							Sign In
						</Button>
						<Grid container>
							<Grid item xs></Grid>
							<Grid item>
								<Link href="/signup" variant="body2">
									{"Don't have an account? Sign Up"}
								</Link>
							</Grid>
						</Grid>
					</Box>
				</Box>
			</Container>
		</ThemeProvider>
	);
}
