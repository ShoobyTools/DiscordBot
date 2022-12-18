import { ActivityType, Events } from 'discord.js';

export const event = {
	name: Events.ClientReady,
	once: true,
	execute(client) {
		console.log(`${client.user.tag} ready!`);
		client.user.setActivity('/info', { type: ActivityType.Listening });
	},
};