import "./App.css";
import Navigation from './components/Navbar.jsx'

function App() {

	return (
	<div className="flex h-screen flex-col md:flex-row md:overflow-hidden">
    	<div className="w-full flex-none md:w-64">
          <Navigation />
    	</div>
    </div>
	);
}

export default App;
