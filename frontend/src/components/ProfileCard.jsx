import React, { useState } from "react";

function ProfileCard({
	id,
	host,
	username,
	imageSrc,
	github,
	buttontype,
	authId,
}) {
	return (
		<div>
			<a
				href="#"
				className="self-center mx-72 w-96 h-48 flex flex-col items-center bg-white border border-gray-200 rounded-lg shadow md:flex-row md:max-w-xl dark:border-white-700 dark:bg-white-800"
			>
				<img
					className="object-cover ml-2 mr-1 w-full max-w-40 max-h-40 min-w-40 min-h-40 rounded-t-lg h-96 md:h-auto md:w-48 md:rounded-none md:rounded-s-lg"
					src={imageSrc}
					alt=""
				></img>

				<div className="flex flex-col justify-between p-4 leading-normal">
					<h5 className="mb-2 text-2xl font-bold tracking-tight text-black-900 dark:text-black">
						{username}
					</h5>
					{buttontype === "Following" && (
						<button
							onClick={() => {}}
							class="text-white bg-slate-800 hover:bg-orange-500 focus:bg-orange-600 font-medium rounded-lg text-sm px-1 py-1 focus:outline-none dark:focus:bg-orange-500"
						>
							Unfollow
						</button>
					)}

					{buttontype === "Request" && (
						<div className="flex flex-col space-y-1">
							<button
								onClick={() => {}}
								class="text-white bg-slate-800 hover:bg-orange-500 focus:bg-orange-600 font-medium rounded-lg text-sm px-1 py-1 focus:outline-none dark:focus:bg-orange-500"
							>
								Accept
							</button>
							<button
								onClick={() => {}}
								class="text-white bg-slate-800 hover:bg-orange-500 focus:bg-orange-600 font-medium rounded-lg text-sm px-1 py-1 focus:outline-none dark:focus:bg-orange-500"
							>
								Decline
							</button>
						</div>
					)}
				</div>
			</a>
		</div>
	);
}

export default ProfileCard;
