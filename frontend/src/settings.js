module.exports = {
    // modify this if server ip is changed
    SERVER_URL: 'http://localhost:8000',

    CLIENT_URL: 'http://localhost:8080',

    // no vue-routers, use regex instead
    CLIENT_REQUEST_PATH_MODE: /^\/tasks\/[a-zA-Z]{10}$/g
};