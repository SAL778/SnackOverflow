import "./Feed.css";
import React from "react";
import PostCard from "../components/PostCard.jsx";
import temp_image1 from "../assets/snack-logo.png";
import temp_image2 from "../assets/snoop.jpg";

function Feed() {
	// DUMMY DATA
	const posts = [
		{
			id: 1,
			username: "Melon Musk",
			title: "Introducing Snack Overflow!",
			date: "Feb 19th 2024",
			imageSrc: temp_image1,
			description:
				"Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras at massa porta, venenatis turpis consectetur, ultricies velit. Nunc urna ex, condimentum tempor nisl in, accumsan feugiat magna. Ut eros ex, blandit quis dapibus ac, condimentum eu diam. Donec leo sem, tempor quis finibus vel, consequat eget massa. Sed mattis at leo quis vulputate. Quisque et ligula elementum, porttitor odio non, varius quam. Nulla suscipit nibh in turpis venenatis laoreet. Ut luctus eros diam, in posuere mauris rhoncus eget. Vivamus lacinia turpis sem, eu mollis massa lobortis ut. Curabitur cursus eros erat, ac placerat nibh ullamcorper pharetra. Donec gravida vulputate orci, bibendum auctor eros molestie id. Nulla purus leo, dictum ac pharetra sed, lacinia nec ex. Nam sollicitudin, erat quis pellentesque tincidunt, lectus massa lacinia odio, venenatis lacinia nunc nunc semper libero. Praesent tempus rhoncus tempus. Nam mollis eleifend risus a malesuada. Quisque vitae erat in elit hendrerit dignissim nec eu turpis. Aliquam et justo eget erat gravida luctus. Suspendisse potenti. Ut quis sapien tincidunt, facilisis lectus ac, auctor ligula. Morbi mauris metus, ultricies quis sapien eget, dictum blandit neque. Proin at auctor risus, eu aliquet enim. Sed a pharetra nibh, quis vehicula tellus.",
		},
		{
			id: 2,
			username: "John Doe",
			title: "Another Post",
			date: "Feb 20th 2024",
			imageSrc: temp_image2,
			description:
				"This is another post for testing purposes... Snoop Doggy Dogg, my homie!",
		},
		// more posts go here:
	];
	return (
		<div className="feed-container">
			{posts.map((post) => (
				<PostCard
					key={post.id}
					username={post.username}
					title={post.title}
					date={post.date}
					imageSrc={post.imageSrc}
					description={post.description}
				/>
			))}
		</div>
	);
}

export default Feed;
