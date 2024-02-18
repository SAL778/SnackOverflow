import "./App.css";
import Navigation from './components/Navbar.jsx'
import NotificationBar from "./components/Notifbar.jsx";

function App() {

	return (
	<div className="flex h-screen w-screen flex-col md:flex-row md:overflow-hidden bg-gray-200">
    	<div className="flex-none md:w-60">
          <Navigation />
    	</div>
		<div class="flex flex-1 bg-gray-300 mx-4 my-3 h-16 p-4">Header</div>
		<NotificationBar />
    </div>
	);
}

export default App;
