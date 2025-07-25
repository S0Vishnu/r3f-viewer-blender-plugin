import express, { Response } from "express";
const app = express();
const PORT = 4000;

const clients: Response[] = [];

app.use(express.static("viewer/public"));

app.get("/reload", (req, res) => {
  clients.forEach((c) => c.write("data: reload\n\n"));
  clients.length = 0;
  res.send("OK");
});

app.get("/events", (req, res) => {
  res.set({
    "Content-Type": "text/event-stream",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
  });
  res.flushHeaders?.();
  res.write("data: connected\n\n");
  clients.push(res);
});

app.listen(PORT, () =>
  console.log(`Server running at http://localhost:${PORT}`)
);
