import { Client } from "discord.js";
import * as dotenv from "dotenv";
dotenv.config();

console.log("Bot is starting...");

const client = new Client({
	intents: [],
});

client.login(process.env.TOKEN);
