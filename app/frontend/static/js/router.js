// For now, this will handle basic routing.
// We can enhance this later with a more sophisticated router if needed.
const router = {
    routes: {},
    navigate: (path) => {
        window.history.pushState({}, path, window.location.origin + path);
        router.handle();
    },
    handle: () => {
        const path = window.location.pathname;
        const handler = router.routes[path] || router.routes['/404'];
        handler();
    },
    add: (path, handler) => {
        router.routes[path] = handler;
    }
};

window.onpopstate = router.handle;
