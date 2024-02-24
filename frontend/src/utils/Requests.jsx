import axios from "axios";

// ensure the CSRF token is sent with requests
axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.xsrfHeaderName = 'X-CSRFToken';
axios.defaults.withCredentials = true;

const client = axios.create({
  baseURL: "http://127.0.0.1:8000/api/"
  // can add headers here
});


// Function to make a GET request
async function getRequest(apiEndpoint) {
  try {
    const response = await client.get(apiEndpoint, { withCredentials: true });
    return response.data;
  } catch (error) {
    console.error(`Error making GET request to ${apiEndpoint}: `, error.message);
    throw new Error(error.message);
  }
}

// Function to make a POST request
async function postRequest(apiEndpoint, postData) {
  try {
    const response = await client.post(apiEndpoint, postData, { withCredentials: true });
    return response.data;
  } catch (error) {
    console.error(`Error making POST request to ${apiEndpoint}: `, error.message);
    throw new Error(error.message);
  }
}

// Function to make a DELETE request
async function deleteRequest(apiEndpoint) {
  try {
    const response = await client.delete(apiEndpoint, { withCredentials: true });
    return response.data;
  } catch (error) {
    console.error(`Error making DELETE request to ${apiEndpoint}: `, error.message);
    throw new Error(error.message);
  }
}

// Function to make a PUT request
async function putRequest(apiEndpoint) {
  try {
    const response = await client.put(apiEndpoint, { withCredentials: true });
    return response.data;
  } catch (error) {
    console.error(`Error making PUT request to ${apiEndpoint}: `, error.message);
    throw new Error(error.message);
  }
}

export { getRequest, postRequest, deleteRequest, putRequest };