import { NavLink, Link, useNavigate } from "react-router-dom";
import logo from "../assets/snack-logo.png";
// import { Link } from "react-router-dom";
import {
	User,
	UsersThree,
	Sparkle,
	UploadSimple,
	SignOut,
} from "@phosphor-icons/react";
import { useAuth } from "../utils/Auth.jsx";
import { useEffect, useState } from "react";
import { getRequest } from "../utils/Requests.jsx";

// The navigation and links components are adapted and modified from the "Learning Next.js" tutorial written by
// Vercel inc. and their contributors. Both links below are the source component pages from the repository which showcases the finished
// example webpage after the tutorial is completed. Accessed 2024-02-22
// https://github.com/vercel/next-learn/blob/main/dashboard/final-example/app/ui/dashboard/sidenav.tsx
// https://github.com/vercel/next-learn/blob/main/dashboard/final-example/app/ui/dashboard/nav-links.tsx

function Links() {
	const objects = [
		{
			content: "Profile",
			href: "/profile",
			icon: User,
		},
		{ content: "Feed", href: "/feed", icon: UsersThree },
		{ content: "Explore", href: "/explore", icon: Sparkle },
		{ content: "New Post", href: "/newpost", icon: UploadSimple },
		{ content: "Lookup", href: "/lookup", icon: UsersThree },
	];

	return (
		<div>
			{objects.map((object) => {
				const Icons = object.icon;
				return (
					<NavLink
						key={object.content}
						to={object.href}
						className={({ isActive }) =>
							`flex h-[48px] grow items-center justify-center gap-2 p-3 text-sm font-medium md:flex-none md:justify-start md:p-2 md:px-3 ${
								isActive
									? "bg-dark-orange text-white"
									: "bg-white hover:bg-orange-200 hover:text-orange-800"
							}`
						}
					>
						<Icons width="24px" height="24px" />
						<p
							className={({ isActive }) =>
								isActive ? "md:block text-white" : "md:block"
							}
						>
							{object.content}
						</p>
					</NavLink>
				);
			})}
		</div>
	);
}

export default function Navigation() {
	const auth = useAuth();
	const navigate = useNavigate();

	const [intervalId, setIntervalId] = useState(null);


	// poll data from /checkRemoteFollowRequests every 5 seconds
	useEffect(() => {
		const timeout = 10000;	// 10 seconds

		if (auth.user) {
			const id = setInterval(async () => {
				await getRequest("checkRemoteFollowRequests/")
			}, timeout);

			setIntervalId(id);

		} else {
			clearInterval(id);
		}

		// Cleanup function to clear the interval when the component unmounts
		return () => {
			clearInterval(intervalId);
		};
	}, []);


	const handleLogout = async (e) => {
		e.preventDefault();
		await auth.logout();
		clearInterval(intervalId);
		navigate("/login");
	};

	return (
		<div className="flex h-full flex-col px-3 py-4">
			<Link
				className="mb-2 flex h-20 items-end rounded-md bg-white p-4 shadow-md"
				to="/feed"
			>
				<div>
					<img
						className="object-center"
						src={logo}
						alt="Snack Overflow icon"
						width={250}
						height={40}
					/>
				</div>
			</Link>
			<div className="flex grow flex-row justify-between space-x-2 shadow-md md:flex-col md:space-x-0">
				<Links />
				<div className="hidden h-auto w-full grow bg-white md:block"></div>
				<button
					onClick={handleLogout}
					className="flex h-[48px] w-full grow items-center rounded-md justify-center gap-2 bg-white shadow-md p-3 text-sm font-medium hover:bg-orange-200 hover:text-orange-800 md:flex-none md:justify-start md:p-2 md:px-3"
				>
					<SignOut style={{ width: "24px", height: "24px" }} />
					<div className="hidden md:block">Sign Out</div>
				</button>
			</div>
		</div>
	);
}
