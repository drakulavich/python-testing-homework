const jsonServer = require("json-server");
const server = jsonServer.create();
const router = jsonServer.router(
  { users: [{ id: 1, name: "John Doe" }],
    photos: [{ id: 10, url: "http://img.ur/awesome.jpeg" }],
  }
);
const middlewares = jsonServer.defaults();

server.use(middlewares);

server.use(router);
server.listen(4242, () => {
  console.log("JSON Server is running");
});
