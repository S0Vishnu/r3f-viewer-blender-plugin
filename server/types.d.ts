import { Response } from "express";
declare global {
  type SSEClient = Response;
}
