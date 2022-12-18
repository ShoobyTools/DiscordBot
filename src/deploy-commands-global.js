import { REST, Routes } from 'discord.js';
import fs from 'fs';
import * as dotenv from 'dotenv';
dotenv.config({path: `${__dirname}/../.env`});

const commands = [];

const commandFiles = fs.readdirSync(`${__dirname}/commands`).filter(file => file.endsWith('.js'));

(async () => {
	for (const file of commandFiles) {
		const { command } = await import(`${__dirname}/commands/${file}`);
		commands.push(command.data.toJSON());
	}

	const rest = new REST({ version: '10' }).setToken(process.env.TOKEN);

	try {
		console.log(`Started refreshing ${commands.length} application (/) commands.`);

		const data = await rest.put(
			Routes.applicationCommands(process.env.CLIENT_ID),
			{ body: commands },
		);

		console.log(`Successfully reloaded ${data.length} application (/) commands.`);
	} catch (error) {
		console.error(error);
	}
})();