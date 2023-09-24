const jsonServer = require("json-server");
const server = jsonServer.create();
const router = jsonServer.router(
  { users: [{ id: 1, name: "John Doe" }],
    photos: [{ id: 10, url: "http://img.ur/awesome.jpeg" }],
  }
);
const middlewares = jsonServer.defaults();

// Middleware to introduce a delay for requests to /photos
server.use((req, res, next) => {
  if (req.path.startsWith('/photos')) {
    // Introduce a delay of, for example, 2000ms (2 seconds) for /photos requests
    setTimeout(next, 2000);
  } else {
    next();
  }
});

server.use(middlewares);
server.use(router);

server.listen(4242, () => {
  console.log("JSON Server is running");
});
