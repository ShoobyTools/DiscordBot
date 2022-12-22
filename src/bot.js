import { Client, Collection, Events, GatewayIntentBits } from 'discord.js';
import fs from 'fs';
import path from 'path';
import { stopQueueDriver } from './commands/queue';
import * as dotenv from 'dotenv';
dotenv.config();

const client = new Client({ intents: [GatewayIntentBits.Guilds] });
client.commands = new Collection();


(async () => {
	const commandsPath = path.join(__dirname, 'commands');
	const commandFiles = fs.readdirSync(commandsPath).filter(file => file.endsWith('.js'));
	for (const file of commandFiles) {
		const filePath = path.join(commandsPath, file);
		const { command } = await import(filePath);
		if ('data' in command && 'execute' in command) {
			client.commands.set(command.data.name, command);
		} else {
			console.log(`[WARNING] The command at ${filePath} is missing a required "data" or "execute" property.`);
		}
	}
	const eventsPath = path.join(__dirname, 'events');
	const eventFiles = fs.readdirSync(eventsPath).filter(file => file.endsWith('.js'));

	for (const file of eventFiles) {
		const filePath = path.join(eventsPath, file);
		const { event } = await import(filePath);
		if (event.once) {
			client.once(event.name, (...args) => event.execute(...args));
		} else {
			client.on(event.name, (...args) => event.execute(...args));
		}
	}
})();

client.on(Events.InteractionCreate, async (interaction) => {
	if (!interaction.isButton()) return;
	if (interaction.customId === 'stop-queue') {
		await stopQueueDriver();
		await interaction.update({ content: "Done monitoring queue.", components: [] });
	}
});

client.login(process.env.TOKEN);