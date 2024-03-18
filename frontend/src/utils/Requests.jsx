import axios from "axios";

// ensure the CSRF token is sent with requests
axios.defaults.xsrfCookieName = "csrftoken";
axios.defaults.xsrfHeaderName = "X-CSRFToken";
axios.defaults.withCredentials = true;
axios.defaults.withXSRFToken = true;

let baseURL = "http://127.0.0.1:8000/api/";
// let baseURL =
// 	"https://snackoverflow-deployment-test-37cd2b94a62f.herokuapp.com/api/";

// if (process.env.NODE_ENV === "development") {
// 	baseURL = "http://127.0.0.1:8000/api/";
// }

const client = axios.create({
	baseURL: baseURL,
	// can add headers here
});

// Function to make a GET request
async function getRequest(apiEndpoint) {
	try {
		const response = await client.get(apiEndpoint, { withCredentials: true });
		return response.data;
	} catch (error) {
		console.error(
			`Error making GET request to ${apiEndpoint}: `,
			error.message
		);
		throw new Error(error.message);
	}
}
// Function to make a POST request
async function postRequest(apiEndpoint, postData, isJson = false) {
	try {
		const config = {
			withCredentials: true,
		};

		if (isJson) {
			config.headers = {
				"Content-Type": "application/json",
			};
		}

		const response = await client.post(apiEndpoint, postData, config);
		return response.data;
	} catch (error) {
		console.error(
			`Error making POST request to ${apiEndpoint}: `,
			error.message
		);
		const value = error?.response?.request?.responseText;
		if (value !== undefined) {
			throw new Error(value);
		} else {
			throw new Error(error.message);
		}
	}
}

// Function to make a DELETE request
async function deleteRequest(apiEndpoint) {
	try {
		const response = await client.delete(apiEndpoint, {
			withCredentials: true,
		});
		return response.data;
	} catch (error) {
		console.error(
			`Error making DELETE request to ${apiEndpoint}: `,
			error.message
		);
		throw new Error(error.message);
	}
}

// Function to make a PUT request
async function putRequest(apiEndpoint, data) {
	try {
		const response = await client.put(apiEndpoint, data, {
			withCredentials: true,
		});
		return response.data;
	} catch (error) {
		console.error(
			`Error making PUT request to ${apiEndpoint}: `,
			error.message
		);
		throw new Error(error.message);
	}
}

export { getRequest, postRequest, deleteRequest, putRequest };
