import express from "express";
import type { Response } from "express";
import path from "path";

const app = express();
const PORT = 4000;

const clients: Response[] = [];

app.use(express.static(path.join(__dirname, "viewer/public")));

app.get("/reload", (req, res) => {
  clients.forEach((c) => c.write("data: reload\n\n"));
  clients.length = 0;
  res.send("OK");
});

app.get("/events", (req, res) => {
  res.setHeader("Content-Type", "text/event-stream");
  res.setHeader("Cache-Control", "no-cache");
  res.setHeader("Connection", "keep-alive");

  res.flushHeaders?.();
  res.write("data: connected\n\n");

  clients.push(res);
});

app.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
});
