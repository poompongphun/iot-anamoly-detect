import axios from "axios";

const instance = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  timeout: 10000,
});

// instance.interceptors.request.use(
//   (config) => {
//     // Add any custom request headers here if needed
//     return config;
//   },
//   (error) => {
//     // Handle request error
//     return Promise.reject(error);
//   }
// );

// instance.interceptors.response.use(
//   (response) => {
//     // Handle successful response
//     return response.data;
//   },
//   (error) => {
//     // Handle response error
//     return Promise.reject(error);
//   }
// );

export default instance;