const API_BASE_URL = "http://localhost:8000";

// API endpoints
const API_ENDPOINTS = {
    LOGIN: "/auth/login_admin",

    ADD_PRODUCT: "/products",
    ADD_SOLD_PRODUCT: "/sold",
    GET_PRODUCTS: "/products",
    GET_SOLD_PRODUCTS: "/sold",
    UPDATE_PRODUCT: "/products",
    DELETE_PRODUCT: "/products",
}

export { API_BASE_URL, API_ENDPOINTS };