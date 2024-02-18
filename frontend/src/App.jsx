import "./App.css";
import Navigation from './components/Navbar.jsx'

function App() {

	return (
	<div className="flex h-screen w-screen flex-col md:flex-row md:overflow-hidden">
    	<div className="flex-none md:w-60">
          <Navigation />
    	</div>
		<div class="flex flex-1 bg-gray-300 h-16 p-4">Header</div>
    </div>
	);
}

export default App;
